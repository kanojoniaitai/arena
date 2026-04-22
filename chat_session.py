from __future__ import annotations

import gc
import time
from dataclasses import dataclass, field
from typing import Any

from llama_cpp import Llama

from arena.engine import stream_answer
from arena.models import ModelSpec


@dataclass
class ChatMessage:
    role: str
    content: str
    timestamp: float = field(default_factory=time.time)


class ChatSession:
    def __init__(
        self,
        spec: ModelSpec | None = None,
        n_ctx: int = 8192,
        n_gpu_layers: int = -1,
        n_batch: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
        repeat_penalty: float = 1.05,
    ):
        self.spec = spec
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.n_batch = n_batch
        self.temperature = temperature
        self.top_p = top_p
        self.repeat_penalty = repeat_penalty
        self.llm: Llama | None = None
        self.messages: list[ChatMessage] = []
        self.system_prompt = ""
        self.load_error: str = ""

    def load_model(self, spec: ModelSpec | None = None) -> bool:
        if spec:
            self.spec = spec
        if not self.spec:
            self.load_error = "未选择模型"
            return False
        if self.llm:
            self.unload_model()
        try:
            self.llm = Llama(
                model_path=self.spec.path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                n_batch=self.n_batch,
                verbose=False,
            )
            self.load_error = ""
            return True
        except Exception as e:
            self.load_error = str(e)
            return False

    def unload_model(self) -> None:
        if self.llm:
            self.llm.close()
            self.llm = None
        gc.collect()

    def set_system_prompt(self, prompt: str) -> None:
        self.system_prompt = prompt.strip()

    def add_user_message(self, content: str) -> None:
        self.messages.append(ChatMessage(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        self.messages.append(ChatMessage(role="assistant", content=content))

    def clear_history(self) -> None:
        self.messages = []

    def get_history_text(self) -> str:
        lines = []
        for msg in self.messages:
            prefix = "👤" if msg.role == "user" else "🤖"
            lines.append(f"{prefix} {msg.content}")
        return "\n\n".join(lines)

    def generate_response(
        self,
        user_input: str,
        max_tokens: int = 2048,
        seed: int = -1,
    ) -> str:
        if not self.llm:
            return "[错误] 模型未加载"
        self.add_user_message(user_input)
        system = self.system_prompt or "你是一名专业、准确、简洁的中文助手。"
        messages = [{"role": "system", "content": system}]
        for msg in self.messages:
            messages.append({"role": msg.role, "content": msg.content})
        response_chunks: list[str] = []
        for token in stream_answer(
            llm=self.llm,
            messages=messages,
            max_tokens=max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            repeat_penalty=self.repeat_penalty,
            seed=seed,
        ):
            response_chunks.append(token)
        response = "".join(response_chunks).strip()
        self.add_assistant_message(response)
        return response

    def get_model_info(self) -> dict[str, Any]:
        if not self.spec:
            return {"name": "未选择", "loaded": False}
        return {
            "name": self.spec.label,
            "path": self.spec.path,
            "params": self.spec.params,
            "quant": self.spec.quant,
            "size_gb": self.spec.size_gb,
            "loaded": self.llm is not None,
            "error": self.load_error,
        }
