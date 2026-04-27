from __future__ import annotations

import asyncio
import gc
import json
import queue
import threading
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from llama_cpp import Llama

from backend.config import DEFAULT_SYSTEM_PROMPT, LLM_PARAMS
from backend.engine import stream_answer
from backend.models import get_model_by_name
from backend.storage import load_groups

router = APIRouter()

executor = ThreadPoolExecutor(max_workers=4)

GROUP_CHAT_SUFFIX = (
    "\n\n【群聊提示】你正在一个群聊中。除了回复用户，你也可以对其他角色的发言"
    "做出回应、吐槽、反驳或附和。如果有人说了你不同意的话，大胆反驳！"
)


def _load_model(model_path: str) -> Llama:
    return Llama(
        model_path=model_path,
        n_ctx=LLM_PARAMS["n_ctx"],
        n_gpu_layers=LLM_PARAMS["n_gpu_layers"],
        n_batch=LLM_PARAMS["n_batch"],
        verbose=False,
    )


def _get_model_params(spec):
    return {
        "max_tokens": spec.max_tokens if spec.max_tokens is not None else LLM_PARAMS["max_tokens"],
        "temperature": spec.temperature if spec.temperature is not None else LLM_PARAMS["temperature"],
        "top_p": spec.top_p if spec.top_p is not None else LLM_PARAMS["top_p"],
        "repeat_penalty": spec.repeat_penalty if spec.repeat_penalty is not None else LLM_PARAMS["repeat_penalty"],
        "seed": LLM_PARAMS["seed"],
    }


class ModelManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.infer_lock = threading.Lock()
        self.current_path: str | None = None
        self.llm: Llama | None = None

    def get_model(self, path: str) -> Llama:
        with self.lock:
            if self.current_path == path and self.llm is not None:
                return self.llm
            
            if self.llm is not None:
                try:
                    if hasattr(self.llm, 'close'):
                        self.llm.close()
                except Exception:
                    pass
                finally:
                    self.llm = None
                    self.current_path = None
                    gc.collect()

            self.llm = _load_model(path)
            self.current_path = path
            return self.llm


model_manager = ModelManager()


def _stream_model_to_queue(
    llm: Llama,
    messages: list[dict[str, str]],
    q: queue.Queue,
    spec=None,
) -> None:
    params = _get_model_params(spec) if spec else {
        "max_tokens": LLM_PARAMS["max_tokens"],
        "temperature": LLM_PARAMS["temperature"],
        "top_p": LLM_PARAMS["top_p"],
        "repeat_penalty": LLM_PARAMS["repeat_penalty"],
        "seed": LLM_PARAMS["seed"],
    }
    try:
        with model_manager.infer_lock:
            for token in stream_answer(
                llm=llm,
                messages=messages,
                **params
            ):
                q.put(token)
    except Exception as exc:
        q.put(exc)
    finally:
        q.put(None)


def _build_messages(
    system_prompt: str,
    message: str,
    history: list[dict[str, str]],
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    for h in history:
        role = h.get("role", "user")
        content = h.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})
    return messages


def _build_group_messages(
    system_prompt: str,
    message: str,
    history: list[dict[str, str]],
    previous_responses: list[dict[str, str]],
) -> list[dict[str, str]]:
    group_prompt = system_prompt + GROUP_CHAT_SUFFIX
    messages: list[dict[str, str]] = [{"role": "system", "content": group_prompt}]

    for h in history:
        role = h.get("role", "user")
        content = h.get("content", "")
        sender = h.get("sender", "")
        display_name = h.get("display_name", "")
        if not content:
            continue
        if role == "user":
            messages.append({"role": "user", "content": content})
        elif role == "assistant":
            label = display_name or sender or "某人"
            messages.append({"role": "user", "content": f"【{label}说】：{content}"})

    if previous_responses:
        context_parts = []
        for resp in previous_responses:
            label = resp.get("display_name", resp.get("model_name", "某人"))
            context_parts.append(f"【{label}说】：{resp['content']}")
        context = "\n\n".join(context_parts)
        user_content = f"其他角色的发言：\n{context}\n\n用户消息：{message}"
    else:
        user_content = message

    messages.append({"role": "user", "content": user_content})
    return messages


async def _safe_send_json(websocket: WebSocket, data: dict) -> bool:
    """安全地发送 JSON 消息，如果连接已关闭则返回 False"""
    try:
        await websocket.send_json(data)
        return True
    except (WebSocketDisconnect, RuntimeError):
        return False


async def _run_model_stream(
    websocket: WebSocket,
    model_name: str,
    messages: list[dict[str, str]],
    stream_type: str,
    extra_fields: dict,
) -> str:
    spec = get_model_by_name(model_name)
    if spec is None:
        raise ValueError(f"Model '{model_name}' not found")

    loop = asyncio.get_running_loop()
    llm = await loop.run_in_executor(executor, model_manager.get_model, spec.path)

    q: queue.Queue = queue.Queue()
    thread = threading.Thread(
        target=_stream_model_to_queue,
        args=(llm, messages, q, spec),
        daemon=True,
    )
    thread.start()

    full_content = []
    while True:
        try:
            item = await loop.run_in_executor(None, q.get, True, 0.1)
            if item is None:
                return "".join(full_content)
            if isinstance(item, Exception):
                raise item
            
            full_content.append(item)
            payload = {
                "type": stream_type,
                "model_name": model_name,
                "token": item,
            }
            payload.update(extra_fields)
            # 使用安全发送，如果连接断开则提前返回
            if not await _safe_send_json(websocket, payload):
                return "".join(full_content)
        except queue.Empty:
            continue


@router.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            msg_type = data.get("type")
            if msg_type != "chat":
                await websocket.send_json({"type": "error", "message": f"Unknown type: {msg_type}"})
                continue

            chat_type = data.get("chat_type", "private")
            model_name = data.get("model_name", "")
            group_id = data.get("group_id", "")
            message = data.get("message", "")
            history = data.get("history", [])

            if chat_type == "private":
                await _handle_private(websocket, model_name, message, history)
            elif chat_type == "group":
                await _handle_group(websocket, group_id, message, history)
            else:
                await websocket.send_json({"type": "error", "message": f"Unknown chat_type: {chat_type}"})

    except WebSocketDisconnect:
        pass


async def _handle_private(
    websocket: WebSocket,
    model_name: str,
    message: str,
    history: list[dict[str, str]],
):
    spec = get_model_by_name(model_name)
    if spec is None:
        await _safe_send_json(websocket, {"type": "error", "message": f"Model '{model_name}' not found"})
        return

    system_prompt = spec.system_prompt or DEFAULT_SYSTEM_PROMPT
    messages = _build_messages(system_prompt, message, history)

    try:
        await _run_model_stream(
            websocket,
            model_name,
            messages,
            "ai_stream_token",
            {}
        )
        await _safe_send_json(websocket, {
            "type": "ai_complete",
            "model_name": model_name,
        })
    except (WebSocketDisconnect, RuntimeError):
        # 连接已断开，静默处理
        pass
    except Exception as exc:
        await _safe_send_json(websocket, {"type": "error", "message": str(exc)})


async def _handle_group(
    websocket: WebSocket,
    group_id: str,
    message: str,
    history: list[dict[str, str]],
):
    groups = load_groups()
    group = None
    for g in groups:
        if g.get("id") == group_id:
            group = g
            break

    if group is None:
        await _safe_send_json(websocket, {"type": "error", "message": f"Group '{group_id}' not found"})
        return

    members = group.get("members", [])
    if not members:
        await _safe_send_json(websocket, {"type": "error", "message": "Group has no members"})
        return

    accumulated_responses: list[dict[str, str]] = []

    for member_name in members:
        spec = get_model_by_name(member_name)
        if spec is None:
            continue

        system_prompt = spec.system_prompt or DEFAULT_SYSTEM_PROMPT
        display_name = spec.display_name or member_name
        msgs = _build_group_messages(system_prompt, message, history, accumulated_responses)

        try:
            content = await _run_model_stream(
                websocket,
                member_name,
                msgs,
                "group_stream_token",
                {"display_name": display_name}
            )
            result = {
                "type": "group_reply",
                "model_name": member_name,
                "display_name": display_name,
                "content": content,
            }
            if not await _safe_send_json(websocket, result):
                return  # 连接已断开，提前退出

            accumulated_responses.append({
                "model_name": member_name,
                "display_name": display_name,
                "content": content,
            })
        except (WebSocketDisconnect, RuntimeError):
            # 连接已断开，提前退出
            return
        except Exception as exc:
            if not await _safe_send_json(websocket, {"type": "error", "message": str(exc)}):
                return  # 连接已断开，提前退出

    await _safe_send_json(websocket, {"type": "group_complete"})
