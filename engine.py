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


def build_fallback_prompt(system_prompt: str, user_prompt: str) -> str:
    pieces = []
    if system_prompt.strip():
        pieces.append(f"系统要求：\n{system_prompt.strip()}")
    pieces.append(f"用户问题：\n{user_prompt.strip()}")
    pieces.append("请直接给出高质量回答。")
    return "\n\n".join(pieces)


def stream_answer(
    llm: Llama,
    system_prompt: str,
    user_prompt: str,
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
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()},
            ],
            **kwargs,
        )
        for chunk in stream:
            token = extract_stream_text(chunk)
            if token:
                yield token
        return
    except Exception:
        yield "\n\n[提示] chat 模式不可用，已切换为 completion 兼容模式。\n\n"
        fallback_prompt = build_fallback_prompt(system_prompt, user_prompt)
        stream = llm.create_completion(prompt=fallback_prompt, **kwargs)
        for chunk in stream:
            token = extract_stream_text(chunk)
            if token:
                yield token


def run_single_model(
    spec: ModelSpec,
    prompt: str,
    system_prompt: str,
    n_ctx: int,
    max_tokens: int,
    temperature: float,
    top_p: float,
    repeat_penalty: float,
    n_gpu_layers: int,
    n_batch: int,
    seed: int,
    result_container: dict[str, Any],
) -> None:
    started_at = time.perf_counter()
    result_container["status"] = "加载中"
    result_container["detail"] = "正在载入模型到 llama.cpp。"
    llm: Llama | None = None
    try:
        llm = Llama(
            model_path=spec.path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            n_batch=n_batch,
            verbose=False,
        )
        result_container["status"] = "生成中"
        result_container["detail"] = "当前模型仅使用系统提示词 + 当前用户指令，和其他模型完全隔离。"
        answer_chunks: list[str] = []
        token_count = 0
        gen_start = time.perf_counter()
        for token in stream_answer(
            llm=llm,
            system_prompt=system_prompt,
            user_prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=repeat_penalty,
            seed=seed,
        ):
            answer_chunks.append(token)
            token_count += 1
            result_container["answer"] = "".join(answer_chunks).strip()
        gen_elapsed = time.perf_counter() - gen_start
        total_elapsed = time.perf_counter() - started_at
        tps = token_count / gen_elapsed if gen_elapsed > 0 else 0.0
        result_container["status"] = "已完成"
        result_container["detail"] = "本轮回答已完成。"
        result_container["elapsed"] = f"{total_elapsed:.1f}s"
        result_container["perf"] = f"{tps:.1f} t/s"
        result_container["token_count"] = token_count
        result_container["tps"] = tps
    except Exception as exc:
        total_elapsed = time.perf_counter() - started_at
        result_container["status"] = "失败"
        result_container["detail"] = f"运行失败：{exc}"
        result_container["answer"] = ""
        result_container["elapsed"] = f"{total_elapsed:.1f}s"
    finally:
        if llm is not None:
            llm.close()
        gc.collect()
