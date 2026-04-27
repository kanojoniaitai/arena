from __future__ import annotations

from typing import Any, Generator

from llama_cpp import Llama


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
