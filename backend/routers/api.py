from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models import discover_models, get_model_by_name
from backend.storage import (
    load_chat_history, load_groups, save_chat_history, save_groups,
    load_model_configs, save_model_configs,
)

router = APIRouter(prefix="/api")


class ModelUpdateRequest(BaseModel):
    avatar: str = ""
    system_prompt: str = ""
    display_name: str = ""
    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    repeat_penalty: float | None = None


class GroupCreateRequest(BaseModel):
    name: str
    members: list[str]


class ChatHistorySaveRequest(BaseModel):
    conv_id: str
    messages: list[dict]


class BatchHistorySaveRequest(BaseModel):
    history: dict[str, list[dict]]


@router.get("/models")
async def list_models():
    from backend.config import LLM_PARAMS
    models = discover_models()
    return [
        {
            "name": Path(m.path).stem,
            "display_name": m.display_name or Path(m.path).stem,
            "avatar": m.avatar,
            "system_prompt": m.system_prompt,
            "params": m.params,
            "quant": m.quant,
            "size_gb": m.size_gb,
            "temperature": m.temperature if hasattr(m, 'temperature') and m.temperature is not None else LLM_PARAMS["temperature"],
            "max_tokens": m.max_tokens if hasattr(m, 'max_tokens') and m.max_tokens is not None else LLM_PARAMS["max_tokens"],
            "top_p": m.top_p if hasattr(m, 'top_p') and m.top_p is not None else LLM_PARAMS["top_p"],
            "repeat_penalty": m.repeat_penalty if hasattr(m, 'repeat_penalty') and m.repeat_penalty is not None else LLM_PARAMS["repeat_penalty"],
        }
        for m in models
    ]


@router.put("/models/{model_name}")
async def update_model(model_name: str, body: ModelUpdateRequest):
    spec = get_model_by_name(model_name)
    if spec is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    configs = load_model_configs()
    if model_name not in configs:
        configs[model_name] = {}
    configs[model_name]["avatar"] = body.avatar
    configs[model_name]["system_prompt"] = body.system_prompt
    if body.display_name:
        configs[model_name]["display_name"] = body.display_name
    if body.temperature is not None:
        configs[model_name]["temperature"] = body.temperature
    if body.max_tokens is not None:
        configs[model_name]["max_tokens"] = body.max_tokens
    if body.top_p is not None:
        configs[model_name]["top_p"] = body.top_p
    if body.repeat_penalty is not None:
        configs[model_name]["repeat_penalty"] = body.repeat_penalty
    save_model_configs(configs)
    return {"status": "ok"}


@router.get("/groups")
async def list_groups():
    return load_groups()


@router.post("/groups")
async def create_group(body: GroupCreateRequest):
    groups = load_groups()
    new_group = {
        "id": str(uuid.uuid4()),
        "name": body.name,
        "members": body.members,
    }
    groups.append(new_group)
    save_groups(groups)
    return new_group


@router.delete("/groups/{group_id}")
async def delete_group(group_id: str):
    groups = load_groups()
    filtered = [g for g in groups if g.get("id") != group_id]
    if len(filtered) == len(groups):
        raise HTTPException(status_code=404, detail=f"Group '{group_id}' not found")
    save_groups(filtered)
    return {"status": "ok"}


@router.get("/history")
async def get_chat_history():
    return load_chat_history()


@router.post("/history")
async def save_history(body: ChatHistorySaveRequest):
    history = load_chat_history()
    history[body.conv_id] = body.messages
    save_chat_history(history)
    return {"status": "ok"}


@router.post("/history/batch")
async def save_history_batch(body: BatchHistorySaveRequest):
    save_chat_history(body.history)
    return {"status": "ok"}


@router.delete("/history/{conv_id}")
async def delete_history(conv_id: str):
    history = load_chat_history()
    if conv_id in history:
        del history[conv_id]
        save_chat_history(history)
    return {"status": "ok"}
