from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models import discover_models, get_model_by_name
from backend.storage import (
    load_chat_history, load_groups, save_chat_history, save_groups,
    load_model_configs, save_model_configs,
    load_debates, save_debates, load_stories, save_stories,
    load_undercovers, save_undercovers, load_werewolves, save_werewolves,
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


class DebateCreateRequest(BaseModel):
    topic: str
    pro_model: str
    con_model: str
    max_rounds: int = 5


class DebateVoteRequest(BaseModel):
    winner: str


class StoryCreateRequest(BaseModel):
    name: str
    members: list[str]


class UndercoverCreateRequest(BaseModel):
    name: str
    members: list[str]
    civilian_word: str
    undercover_word: str


class UndercoverEliminateRequest(BaseModel):
    model_name: str


class WerewolfCreateRequest(BaseModel):
    name: str
    members: list[str]


class WerewolfPhaseRequest(BaseModel):
    phase: str
    sub_phase: str = ""


class WerewolfEliminateRequest(BaseModel):
    model_name: str


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


@router.get("/debates")
async def list_debates():
    return load_debates()


@router.post("/debates")
async def create_debate(body: DebateCreateRequest):
    debates = load_debates()
    new_debate = {
        "id": str(uuid.uuid4()),
        "topic": body.topic,
        "pro_model": body.pro_model,
        "con_model": body.con_model,
        "max_rounds": body.max_rounds,
        "current_round": 1,
        "pro_score": 0,
        "con_score": 0,
    }
    debates.append(new_debate)
    save_debates(debates)
    return new_debate


@router.put("/debates/{debate_id}/next-round")
async def next_debate_round(debate_id: str):
    debates = load_debates()
    debate = None
    for d in debates:
        if d.get("id") == debate_id:
            debate = d
            break
    if debate is None:
        raise HTTPException(status_code=404, detail=f"Debate '{debate_id}' not found")
    debate["current_round"] = debate.get("current_round", 1) + 1
    save_debates(debates)
    return debate


@router.post("/debates/{debate_id}/vote")
async def vote_debate(debate_id: str, body: DebateVoteRequest):
    debates = load_debates()
    debate = None
    for d in debates:
        if d.get("id") == debate_id:
            debate = d
            break
    if debate is None:
        raise HTTPException(status_code=404, detail=f"Debate '{debate_id}' not found")
    if body.winner == "pro":
        debate["pro_score"] = debate.get("pro_score", 0) + 1
    elif body.winner == "con":
        debate["con_score"] = debate.get("con_score", 0) + 1
    save_debates(debates)
    return debate


@router.delete("/debates/{debate_id}")
async def delete_debate(debate_id: str):
    debates = load_debates()
    filtered = [d for d in debates if d.get("id") != debate_id]
    if len(filtered) == len(debates):
        raise HTTPException(status_code=404, detail=f"Debate '{debate_id}' not found")
    save_debates(filtered)
    return {"status": "ok"}


@router.get("/stories")
async def list_stories():
    return load_stories()


@router.post("/stories")
async def create_story(body: StoryCreateRequest):
    stories = load_stories()
    new_story = {
        "id": str(uuid.uuid4()),
        "name": body.name,
        "members": body.members,
    }
    stories.append(new_story)
    save_stories(stories)
    return new_story


@router.delete("/stories/{story_id}")
async def delete_story(story_id: str):
    stories = load_stories()
    filtered = [s for s in stories if s.get("id") != story_id]
    if len(filtered) == len(stories):
        raise HTTPException(status_code=404, detail=f"Story '{story_id}' not found")
    save_stories(filtered)
    return {"status": "ok"}


@router.get("/undercovers")
async def list_undercovers():
    return load_undercovers()


@router.post("/undercovers")
async def create_undercover(body: UndercoverCreateRequest):
    import random
    undercovers = load_undercovers()
    num_undercover = 1 if len(body.members) < 6 else 2
    undercover_indices = sorted(random.sample(range(len(body.members)), num_undercover))
    new_undercover = {
        "id": str(uuid.uuid4()),
        "name": body.name,
        "members": body.members,
        "civilian_word": body.civilian_word,
        "undercover_word": body.undercover_word,
        "undercover_indices": undercover_indices,
        "current_round": 1,
        "phase": "describe",
        "eliminated": [],
        "game_over": False,
        "winner": None,
    }
    undercovers.append(new_undercover)
    save_undercovers(undercovers)
    return new_undercover


@router.post("/undercovers/{undercover_id}/eliminate")
async def eliminate_undercover_player(undercover_id: str, body: UndercoverEliminateRequest):
    undercovers = load_undercovers()
    game = None
    for u in undercovers:
        if u.get("id") == undercover_id:
            game = u
            break
    if game is None:
        raise HTTPException(status_code=404, detail=f"Undercover game '{undercover_id}' not found")
    if body.model_name not in game.get("eliminated", []):
        game.setdefault("eliminated", []).append(body.model_name)
    alive = [m for m in game["members"] if m not in game["eliminated"]]
    alive_undercover = [game["members"][i] for i in game["undercover_indices"] if game["members"][i] not in game["eliminated"]]
    if len(alive_undercover) == 0:
        game["game_over"] = True
        game["winner"] = "civilian"
    elif len(alive) <= 2:
        game["game_over"] = True
        game["winner"] = "undercover"
    save_undercovers(undercovers)
    return game


@router.put("/undercovers/{undercover_id}/next-round")
async def next_undercover_round(undercover_id: str):
    undercovers = load_undercovers()
    game = None
    for u in undercovers:
        if u.get("id") == undercover_id:
            game = u
            break
    if game is None:
        raise HTTPException(status_code=404, detail=f"Undercover game '{undercover_id}' not found")
    game["current_round"] = game.get("current_round", 1) + 1
    game["phase"] = "describe"
    save_undercovers(undercovers)
    return game


@router.delete("/undercovers/{undercover_id}")
async def delete_undercover(undercover_id: str):
    undercovers = load_undercovers()
    filtered = [u for u in undercovers if u.get("id") != undercover_id]
    if len(filtered) == len(undercovers):
        raise HTTPException(status_code=404, detail=f"Undercover game '{undercover_id}' not found")
    save_undercovers(filtered)
    return {"status": "ok"}


@router.get("/werewolves")
async def list_werewolves():
    return load_werewolves()


@router.post("/werewolves")
async def create_werewolf(body: WerewolfCreateRequest):
    import random
    werewolves = load_werewolves()
    n = len(body.members)
    if n < 4:
        raise HTTPException(status_code=400, detail="Werewolf game requires at least 4 players")
    num_wolves = 1 if n < 7 else 2
    roles_pool = ["werewolf"] * num_wolves
    remaining = n - num_wolves
    special_roles = ["seer", "witch"]
    if remaining >= 3:
        special_roles.append("hunter")
    roles_pool.extend(special_roles[:remaining])
    while len(roles_pool) < n:
        roles_pool.append("villager")
    random.shuffle(roles_pool)
    roles = {body.members[i]: roles_pool[i] for i in range(n)}
    new_werewolf = {
        "id": str(uuid.uuid4()),
        "name": body.name,
        "members": body.members,
        "roles": roles,
        "current_round": 1,
        "phase": "night",
        "sub_phase": "werewolf",
        "eliminated": [],
        "witch_save_used": False,
        "witch_poison_used": False,
        "game_over": False,
        "winner": None,
    }
    werewolves.append(new_werewolf)
    save_werewolves(werewolves)
    return new_werewolf


@router.put("/werewolves/{werewolf_id}/phase")
async def update_werewolf_phase(werewolf_id: str, body: WerewolfPhaseRequest):
    werewolves = load_werewolves()
    game = None
    for w in werewolves:
        if w.get("id") == werewolf_id:
            game = w
            break
    if game is None:
        raise HTTPException(status_code=404, detail=f"Werewolf game '{werewolf_id}' not found")
    game["phase"] = body.phase
    if body.sub_phase:
        game["sub_phase"] = body.sub_phase
    if body.phase == "night" and body.sub_phase == "werewolf":
        game["current_round"] = game.get("current_round", 1) + 1
    save_werewolves(werewolves)
    return game


@router.post("/werewolves/{werewolf_id}/eliminate")
async def eliminate_werewolf_player(werewolf_id: str, body: WerewolfEliminateRequest):
    werewolves = load_werewolves()
    game = None
    for w in werewolves:
        if w.get("id") == werewolf_id:
            game = w
            break
    if game is None:
        raise HTTPException(status_code=404, detail=f"Werewolf game '{werewolf_id}' not found")
    if body.model_name not in game.get("eliminated", []):
        game.setdefault("eliminated", []).append(body.model_name)
    alive_wolves = [m for m in game["members"] if game["roles"].get(m) == "werewolf" and m not in game["eliminated"]]
    alive_good = [m for m in game["members"] if game["roles"].get(m) != "werewolf" and m not in game["eliminated"]]
    if len(alive_wolves) == 0:
        game["game_over"] = True
        game["winner"] = "good"
    elif len(alive_wolves) >= len(alive_good):
        game["game_over"] = True
        game["winner"] = "werewolf"
    save_werewolves(werewolves)
    return game


@router.delete("/werewolves/{werewolf_id}")
async def delete_werewolf(werewolf_id: str):
    werewolves = load_werewolves()
    filtered = [w for w in werewolves if w.get("id") != werewolf_id]
    if len(filtered) == len(werewolves):
        raise HTTPException(status_code=404, detail=f"Werewolf game '{werewolf_id}' not found")
    save_werewolves(filtered)
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


@router.delete("/history/{conv_id}")
async def delete_history(conv_id: str):
    history = load_chat_history()
    if conv_id in history:
        del history[conv_id]
        save_chat_history(history)
    return {"status": "ok"}
