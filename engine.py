from __future__ import annotations

import gc
import time
from typing import Any, Generator

from llama_cpp import Llama

from arena.models import ModelSpec


def extract_stream_text(chunk: dict[str, Any]) -> str:
    choice = chunk.get("choices", [{}])[0]
    if "delta" in choice:
        delta = choice.get("delta") or {}
        return delta.get("content", "") or ""
    if "text" in choice:
        return choice.get("text", "") or ""
    message = choice.get("message") or {}
    return message.get("content", "") or ""


def build_fallback_prompt(messages: list[dict[str, str]]) -> str:
    pieces = []
    for msg in messages:
        role_name = "系统要求" if msg["role"] == "system" else "用户问题" if msg["role"] == "user" else "助手回答"
        pieces.append(f"{role_name}：\n{msg['content'].strip()}")
    pieces.append("请直接给出高质量回答。")
    return "\n\n".join(pieces)


def stream_answer(
    llm: Llama,
    messages: list[dict[str, str]],
    max_tokens: int,
    temperature: float,
    top_p: float,
    repeat_penalty: float,
    seed: int,
) -> Generator[str, None, None]:
    kwargs: dict[str, Any] = {
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "repeat_penalty": repeat_penalty,
        "stream": True,
    }
    if seed >= 0:
        kwargs["seed"] = seed
    try:
        stream = llm.create_chat_completion(
            messages=messages,
            **kwargs,
        )
        for chunk in stream:
            token = extract_stream_text(chunk)
            if token:
                yield token
        return
    except Exception:
        yield "\n\n[提示] chat 模式不可用，已切换为 completion 兼容模式。\n\n"
        fallback_prompt = build_fallback_prompt(messages)
        stream = llm.create_completion(prompt=fallback_prompt, **kwargs)
        for chunk in stream:
            token = extract_stream_text(chunk)
            if token:
                yield token


def run_single_model(
    spec: ModelSpec,
    messages: list[dict[str, str]],
    n_ctx: int,
    max_tokens: int,
    temperature: float,
    top_p: float,
    repeat_penalty: float,
    n_gpu_layers: int,
    n_batch: int,
    seed: int,
) -> Generator[dict[str, Any], None, None]:
    started_at = time.perf_counter()
    result = {"status": "加载中", "detail": "正在载入模型...", "answer": "", "perf": ""}
    yield result
    
    llm: Llama | None = None
    try:
        llm = Llama(
            model_path=spec.path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            n_batch=n_batch,
            verbose=False,
        )
        result["status"] = "生成中"
        yield result
        
        answer_chunks: list[str] = []
        token_count = 0
        gen_start = time.perf_counter()
        
        for token in stream_answer(
            llm=llm,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=repeat_penalty,
            seed=seed,
        ):
            answer_chunks.append(token)
            token_count += 1
            result["answer"] = "".join(answer_chunks).strip()
            # yield selectively to avoid too many UI updates (e.g. every 10 tokens)
            if token_count % 5 == 0:
                yield result
                
        gen_elapsed = time.perf_counter() - gen_start
        total_elapsed = time.perf_counter() - started_at
        tps = token_count / gen_elapsed if gen_elapsed > 0 else 0.0
        
        result["status"] = "已完成"
        result["detail"] = "本轮回答已完成。"
        result["elapsed"] = f"{total_elapsed:.1f}s"
        result["perf"] = f"{tps:.1f} t/s"
        result["tps"] = tps
        yield result
        
    except Exception as exc:
        total_elapsed = time.perf_counter() - started_at
        result["status"] = "失败"
        result["detail"] = f"运行失败：{exc}"
        result["elapsed"] = f"{total_elapsed:.1f}s"
        yield result
        
    finally:
        if llm is not None:
            llm.close()
        gc.collect()
