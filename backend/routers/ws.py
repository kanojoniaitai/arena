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
from backend.storage import load_groups, load_debates, load_stories, load_undercovers, load_werewolves

router = APIRouter()

executor = ThreadPoolExecutor(max_workers=4)

GROUP_CHAT_SUFFIX = (
    "\n\n【群聊提示】你正在一个群聊中。除了回复用户，你也可以对其他角色的发言"
    "做出回应、吐槽、反驳或附和。如果有人说了你不同意的话，大胆反驳！"
)

DEBATE_PRO_SUFFIX = (
    "\n\n【辩论擂台·正方】你正在参加辩论赛，你是正方。"
    "请坚定地从正方立场出发，提出有力的论点和论据，反驳反方的观点。"
    "语言要有说服力和逻辑性。"
)

DEBATE_CON_SUFFIX = (
    "\n\n【辩论擂台·反方】你正在参加辩论赛，你是反方。"
    "请坚定地从反方立场出发，提出有力的论点和论据，反驳正方的观点。"
    "语言要有说服力和逻辑性。"
)

STORY_SUFFIX = (
    "\n\n【故事接龙】你正在参与故事接龙游戏。"
    "请根据前面的故事内容，自然地续写下去。"
    "保持故事风格一致，情节连贯，每次续写2-3个段落。"
    "不要重复已有内容，直接接着写。"
)

UNDERCOVER_CIVILIAN_SUFFIX = (
    "【谁是卧底·平民】你正在参加'谁是卧底'游戏，你是平民。"
    "你的词语是「{word}」。请用1-2句话描述你的词语，"
    "但不能直接说出词语本身或包含词语中的字。"
    "注意不要让卧底猜到你的词语，同时要让其他平民认出你。"
    "每次描述尽量简短精炼，不要重复之前说过的内容。"
)

UNDERCOVER_UNDERCOVER_SUFFIX = (
    "【谁是卧底·卧底】你正在参加'谁是卧底'游戏，你是卧底！"
    "你的词语是「{word}」（平民的词语与你的不同但相似）。"
    "请用1-2句话描述你的词语，但不能直接说出词语本身。"
    "尽量模仿平民的描述方式，不要暴露自己是卧底。"
    "仔细听其他人的描述，猜测平民的词语是什么，然后模仿他们的描述风格。"
)

WEREWOLF_ROLE_PROMPTS = {
    "werewolf": (
        "【狼人杀·狼人】你是狼人！你的目标是消灭所有好人。"
        "夜晚时与同伴商议击杀目标，白天时隐藏身份参与讨论，"
        "引导投票淘汰好人。不要暴露自己的狼人身份！"
        "你的同伴是：{teammates}"
    ),
    "villager": (
        "【狼人杀·村民】你是普通村民。你的目标是找出并投票淘汰所有狼人。"
        "白天时认真分析每个人的发言，找出可疑的人，积极参与投票。"
    ),
    "seer": (
        "【狼人杀·预言家】你是预言家！每个夜晚你可以查验一个人的身份。"
        "利用你的信息引导讨论，但要注意不要被狼人盯上。"
        "你可以选择公开身份或隐藏信息，视情况而定。"
    ),
    "witch": (
        "【狼人杀·女巫】你是女巫！你有一瓶解药和一瓶毒药，各只能使用一次。"
        "夜晚你会知道谁被狼人杀害，可以选择用解药救人。"
        "你也可以使用毒药毒杀一个可疑的人。谨慎使用你的药水！"
    ),
    "hunter": (
        "【狼人杀·猎人】你是猎人！当你被淘汰时，你可以开枪带走一个人。"
        "白天时积极参与讨论找出狼人。如果你被投票淘汰或被狼人杀害，"
        "你可以选择带走一个你认为是狼人的人。"
    ),
}


def _load_model(model_path: str) -> Llama:
    return Llama(
        model_path=model_path,
        n_ctx=LLM_PARAMS["n_ctx"],
        n_gpu_layers=LLM_PARAMS["n_gpu_layers"],
        n_batch=LLM_PARAMS["n_batch"],
        verbose=False,
    )


def _safe_close_llm(llm: Llama) -> None:
    try:
        if hasattr(llm, 'close'):
            llm.close()
    except Exception:
        pass
    finally:
        gc.collect()


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


def _run_model_sync(model_name: str, messages: list[dict[str, str]]) -> str:
    spec = get_model_by_name(model_name)
    if spec is None:
        raise ValueError(f"Model '{model_name}' not found")
    llm = model_manager.get_model(spec.path)
    params = _get_model_params(spec)
    try:
        chunks: list[str] = []
        with model_manager.infer_lock:
            for token in stream_answer(
                llm=llm,
                messages=messages,
                **params
            ):
                chunks.append(token)
        return "".join(chunks)
    finally:
        pass


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


def _build_undercover_messages(
    word: str,
    is_undercover: bool,
    history: list[dict[str, str]],
    previous_descriptions: list[dict[str, str]],
    round_num: int,
    phase: str,
) -> list[dict[str, str]]:
    if is_undercover:
        system_content = UNDERCOVER_UNDERCOVER_SUFFIX.format(word=word)
    else:
        system_content = UNDERCOVER_CIVILIAN_SUFFIX.format(word=word)
    messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]

    for h in history:
        role = h.get("role", "user")
        content = h.get("content", "")
        if not content:
            continue
        if role == "user":
            messages.append({"role": "user", "content": content})
        elif role == "assistant":
            sender = h.get("display_name", h.get("sender", "玩家"))
            messages.append({"role": "user", "content": f"【{sender}说】：{content}"})

    if previous_descriptions:
        desc_parts = []
        for desc in previous_descriptions:
            label = desc.get("display_name", desc.get("model_name", "玩家"))
            desc_parts.append(f"【{label}说】：{desc['content']}")
        context = "\n".join(desc_parts)
        if phase == "describe":
            user_content = f"第{round_num}轮描述。前面玩家的描述：\n{context}\n\n请用1-2句话描述你的词语，不要直接说出词语。"
        else:
            user_content = f"第{round_num}轮投票。所有玩家的描述：\n{context}\n\n请投票选出你认为的卧底，并说明理由。格式：我投票给【玩家名】，理由：..."
        messages.append({"role": "user", "content": user_content})
    else:
        if phase == "describe":
            messages.append({"role": "user", "content": f"第{round_num}轮描述。请用1-2句话描述你的词语，不要直接说出词语。"})
        else:
            messages.append({"role": "user", "content": f"第{round_num}轮投票。请投票选出你认为的卧底，并说明理由。"})

    return messages


def _build_werewolf_messages(
    role: str,
    role_prompt: str,
    history: list[dict[str, str]],
    phase: str,
    sub_phase: str,
    message: str,
    alive_players: list[str],
    teammates: str = "",
) -> list[dict[str, str]]:
    if role == "werewolf" and teammates:
        system_content = role_prompt.format(teammates=teammates)
    else:
        system_content = role_prompt
    messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]

    for h in history:
        role_h = h.get("role", "user")
        content = h.get("content", "")
        if not content:
            continue
        if role_h == "user":
            messages.append({"role": "user", "content": content})
        elif role_h == "assistant":
            sender = h.get("display_name", h.get("sender", "玩家"))
            messages.append({"role": "user", "content": f"【{sender}说】：{content}"})

    alive_str = "、".join(alive_players)
    if phase == "night":
        if sub_phase == "werewolf" and role == "werewolf":
            messages.append({"role": "user", "content": f"天黑了，狼人请睁眼。存活玩家：{alive_str}\n{message}\n请与同伴商议选择击杀目标。"})
        elif sub_phase == "seer" and role == "seer":
            messages.append({"role": "user", "content": f"预言家请睁眼。存活玩家：{alive_str}\n{message}\n请选择你要查验的玩家。"})
        elif sub_phase == "witch" and role == "witch":
            messages.append({"role": "user", "content": f"女巫请睁眼。存活玩家：{alive_str}\n{message}\n请决定是否使用药水。"})
        else:
            messages.append({"role": "user", "content": f"夜晚阶段。{message}"})
    elif phase == "day":
        if sub_phase == "discuss":
            messages.append({"role": "user", "content": f"天亮了，请参与讨论。存活玩家：{alive_str}\n{message}"})
        elif sub_phase == "vote":
            messages.append({"role": "user", "content": f"投票阶段。存活玩家：{alive_str}\n{message}\n请投票选出你认为的狼人，并说明理由。"})
        else:
            messages.append({"role": "user", "content": f"白天阶段。存活玩家：{alive_str}\n{message}"})
    else:
        messages.append({"role": "user", "content": message})

    return messages


def _build_debate_messages(
    topic: str,
    history: list[dict[str, str]],
    side: str,
    round_num: int,
) -> list[dict[str, str]]:
    suffix = DEBATE_PRO_SUFFIX if side == "pro" else DEBATE_CON_SUFFIX
    messages: list[dict[str, str]] = [{"role": "system", "content": suffix}]

    for h in history:
        role = h.get("role", "user")
        content = h.get("content", "")
        if not content:
            continue
        if role == "user":
            messages.append({"role": "user", "content": content})
        elif role == "assistant":
            side_label = h.get("side", "")
            sender = h.get("display_name", h.get("sender", "辩手"))
            prefix = f"[正方·{sender}]" if side_label == "pro" else f"[反方·{sender}]"
            messages.append({"role": "user", "content": f"{prefix}：{content}"})

    if round_num == 1:
        messages.append({"role": "user", "content": f"辩题：{topic}\n请陈述你的观点。"})
    else:
        messages.append({"role": "user", "content": f"辩题：{topic}\n请继续第{round_num}轮辩论，反驳对方观点并强化己方论点。"})

    return messages


def _build_story_messages(
    message: str,
    history: list[dict[str, str]],
    accumulated_story: str,
    turn: int,
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [{"role": "system", "content": STORY_SUFFIX}]

    for h in history:
        role = h.get("role", "user")
        content = h.get("content", "")
        if not content:
            continue
        if role == "user":
            messages.append({"role": "user", "content": content})
        elif role == "assistant":
            sender = h.get("display_name", h.get("sender", "叙述者"))
            messages.append({"role": "user", "content": f"【{sender}续写】：{content}"})

    if accumulated_story:
        user_content = f"目前的故事：\n{accumulated_story}\n\n用户指示：{message}\n请接着上面的故事继续写。"
    else:
        user_content = message

    messages.append({"role": "user", "content": user_content})
    return messages


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
            debate_id = data.get("debate_id", "")
            story_id = data.get("story_id", "")
            undercover_id = data.get("undercover_id", "")
            werewolf_id = data.get("werewolf_id", "")
            message = data.get("message", "")
            history = data.get("history", [])

            if chat_type == "private":
                await _handle_private(websocket, model_name, message, history)
            elif chat_type == "group":
                await _handle_group(websocket, group_id, message, history)
            elif chat_type == "debate":
                await _handle_debate(websocket, debate_id, message, history)
            elif chat_type == "story":
                await _handle_story(websocket, story_id, message, history)
            elif chat_type == "undercover":
                await _handle_undercover(websocket, undercover_id, message, history)
            elif chat_type == "werewolf":
                await _handle_werewolf(websocket, werewolf_id, message, history)
            else:
                await websocket.send_json({"type": "error", "message": f"Unknown chat_type: {chat_type}"})

    except WebSocketDisconnect:
        pass


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
        while not q.empty():
            item = q.get_nowait()
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
            await websocket.send_json(payload)
        await asyncio.sleep(0.02)


async def _handle_private(
    websocket: WebSocket,
    model_name: str,
    message: str,
    history: list[dict[str, str]],
):
    spec = get_model_by_name(model_name)
    if spec is None:
        await websocket.send_json({"type": "error", "message": f"Model '{model_name}' not found"})
        return

    system_prompt = spec.system_prompt or DEFAULT_SYSTEM_PROMPT
    messages = _build_messages(system_prompt, message, history)

    loop = asyncio.get_running_loop()
    llm = await loop.run_in_executor(executor, model_manager.get_model, spec.path)

    try:
        q: queue.Queue = queue.Queue()
        thread = threading.Thread(
            target=_stream_model_to_queue,
            args=(llm, messages, q, spec),
            daemon=True,
        )
        thread.start()

        while True:
            while not q.empty():
                item = q.get_nowait()
                if item is None:
                    await websocket.send_json({
                        "type": "ai_complete",
                        "model_name": model_name,
                    })
                    return
                if isinstance(item, Exception):
                    await websocket.send_json({"type": "error", "message": str(item)})
                    return
                await websocket.send_json({
                    "type": "ai_stream_token",
                    "model_name": model_name,
                    "token": item,
                })
            await asyncio.sleep(0.02)
    except Exception as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
    finally:
        pass


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
        await websocket.send_json({"type": "error", "message": f"Group '{group_id}' not found"})
        return

    members = group.get("members", [])
    if not members:
        await websocket.send_json({"type": "error", "message": "Group has no members"})
        return

    loop = asyncio.get_running_loop()
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
            await websocket.send_json(result)

            accumulated_responses.append({
                "model_name": member_name,
                "display_name": display_name,
                "content": content,
            })
        except Exception as exc:
            await websocket.send_json({"type": "error", "message": str(exc)})

    await websocket.send_json({"type": "group_complete"})


async def _handle_debate(
    websocket: WebSocket,
    debate_id: str,
    message: str,
    history: list[dict[str, str]],
):
    debates = load_debates()
    debate = None
    for d in debates:
        if d.get("id") == debate_id:
            debate = d
            break

    if debate is None:
        await websocket.send_json({"type": "error", "message": f"Debate '{debate_id}' not found"})
        return

    pro_model = debate.get("pro_model", "")
    con_model = debate.get("con_model", "")
    topic = debate.get("topic", message)
    round_num = debate.get("current_round", 1)

    loop = asyncio.get_running_loop()

    pro_spec = get_model_by_name(pro_model)
    if pro_spec is None:
        await websocket.send_json({"type": "error", "message": f"Pro model '{pro_model}' not found"})
        return

    pro_display = pro_spec.display_name or pro_model
    pro_msgs = _build_debate_messages(topic, history, "pro", round_num)

    try:
        pro_content = await _run_model_stream(
            websocket,
            pro_model,
            pro_msgs,
            "debate_stream_token",
            {"display_name": pro_display, "side": "pro", "round": round_num}
        )
        await websocket.send_json({
            "type": "debate_reply",
            "model_name": pro_model,
            "display_name": pro_display,
            "content": pro_content,
            "side": "pro",
            "round": round_num,
        })
    except Exception as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
        return

    con_spec = get_model_by_name(con_model)
    if con_spec is None:
        await websocket.send_json({"type": "error", "message": f"Con model '{con_model}' not found"})
        return

    con_display = con_spec.display_name or con_model
    con_history = list(history) + [
        {"role": "assistant", "content": pro_content, "side": "pro", "display_name": pro_display}
    ]
    con_msgs = _build_debate_messages(topic, con_history, "con", round_num)

    try:
        con_content = await _run_model_stream(
            websocket,
            con_model,
            con_msgs,
            "debate_stream_token",
            {"display_name": con_display, "side": "con", "round": round_num}
        )
        await websocket.send_json({
            "type": "debate_reply",
            "model_name": con_model,
            "display_name": con_display,
            "content": con_content,
            "side": "con",
            "round": round_num,
        })
    except Exception as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})

    await websocket.send_json({
        "type": "debate_round_complete",
        "round": round_num,
    })


async def _handle_story(
    websocket: WebSocket,
    story_id: str,
    message: str,
    history: list[dict[str, str]],
):
    stories = load_stories()
    story = None
    for s in stories:
        if s.get("id") == story_id:
            story = s
            break

    if story is None:
        await websocket.send_json({"type": "error", "message": f"Story '{story_id}' not found"})
        return

    members = story.get("members", [])
    if not members:
        await websocket.send_json({"type": "error", "message": "Story has no members"})
        return

    loop = asyncio.get_running_loop()
    accumulated_story = ""

    for h in history:
        if h.get("role") == "assistant" and h.get("content"):
            accumulated_story += h["content"] + "\n"

    for i, member_name in enumerate(members):
        spec = get_model_by_name(member_name)
        if spec is None:
            continue

        display_name = spec.display_name or member_name
        msgs = _build_story_messages(message, history, accumulated_story, i + 1)

        try:
            content = await _run_model_stream(
                websocket,
                member_name,
                msgs,
                "story_stream_token",
                {"display_name": display_name, "turn": i + 1}
            )
            await websocket.send_json({
                "type": "story_reply",
                "model_name": member_name,
                "display_name": display_name,
                "content": content,
                "turn": i + 1,
            })
            accumulated_story += content + "\n"
        except Exception as exc:
            await websocket.send_json({"type": "error", "message": str(exc)})

    await websocket.send_json({"type": "story_cycle_complete"})


async def _handle_undercover(
    websocket: WebSocket,
    undercover_id: str,
    message: str,
    history: list[dict[str, str]],
):
    games = load_undercovers()
    game = None
    for g in games:
        if g.get("id") == undercover_id:
            game = g
            break

    if game is None:
        await websocket.send_json({"type": "error", "message": f"Undercover game '{undercover_id}' not found"})
        return

    if game.get("game_over"):
        await websocket.send_json({"type": "error", "message": "游戏已结束"})
        return

    members = game.get("members", [])
    eliminated = game.get("eliminated", [])
    undercover_indices = game.get("undercover_indices", [])
    civilian_word = game.get("civilian_word", "")
    undercover_word = game.get("undercover_word", "")
    round_num = game.get("current_round", 1)
    phase = game.get("phase", "describe")

    alive_members = [m for m in members if m not in eliminated]
    if not alive_members:
        await websocket.send_json({"type": "error", "message": "没有存活的玩家"})
        return

    loop = asyncio.get_running_loop()
    accumulated_descriptions: list[dict[str, str]] = []

    for member_name in alive_members:
        spec = get_model_by_name(member_name)
        if spec is None:
            continue

        member_idx = members.index(member_name)
        is_undercover = member_idx in undercover_indices
        word = undercover_word if is_undercover else civilian_word
        display_name = spec.display_name or member_name

        msgs = _build_undercover_messages(
            word=word,
            is_undercover=is_undercover,
            history=history,
            previous_descriptions=accumulated_descriptions,
            round_num=round_num,
            phase=phase,
        )

        try:
            content = await _run_model_stream(
                websocket,
                member_name,
                msgs,
                "undercover_stream_token",
                {"display_name": display_name, "round": round_num, "phase": phase, "is_undercover": is_undercover}
            )
            await websocket.send_json({
                "type": "undercover_reply",
                "model_name": member_name,
                "display_name": display_name,
                "content": content,
                "round": round_num,
                "phase": phase,
                "is_undercover": is_undercover,
            })
            accumulated_descriptions.append({
                "model_name": member_name,
                "display_name": display_name,
                "content": content,
            })
        except Exception as exc:
            await websocket.send_json({"type": "error", "message": str(exc)})

    await websocket.send_json({
        "type": "undercover_phase_complete",
        "round": round_num,
        "phase": phase,
    })


async def _handle_werewolf(
    websocket: WebSocket,
    werewolf_id: str,
    message: str,
    history: list[dict[str, str]],
):
    games = load_werewolves()
    game = None
    for g in games:
        if g.get("id") == werewolf_id:
            game = g
            break

    if game is None:
        await websocket.send_json({"type": "error", "message": f"Werewolf game '{werewolf_id}' not found"})
        return

    if game.get("game_over"):
        await websocket.send_json({"type": "error", "message": "游戏已结束"})
        return

    members = game.get("members", [])
    eliminated = game.get("eliminated", [])
    roles = game.get("roles", {})
    phase = game.get("phase", "night")
    sub_phase = game.get("sub_phase", "werewolf")

    alive_members = [m for m in members if m not in eliminated]

    loop = asyncio.get_running_loop()

    if phase == "night":
        if sub_phase == "werewolf":
            target_members = [m for m in alive_members if roles.get(m) == "werewolf"]
        elif sub_phase == "seer":
            target_members = [m for m in alive_members if roles.get(m) == "seer"]
        elif sub_phase == "witch":
            target_members = [m for m in alive_members if roles.get(m) == "witch"]
        else:
            target_members = []
    elif phase == "day":
        target_members = alive_members
    else:
        target_members = alive_members

    if not target_members:
        await websocket.send_json({"type": "error", "message": "当前阶段没有可行动的玩家"})
        return

    alive_display_names = []
    for m in alive_members:
        spec = get_model_by_name(m)
        alive_display_names.append(spec.display_name if spec and spec.display_name else m)

    for member_name in target_members:
        spec = get_model_by_name(member_name)
        if spec is None:
            continue

        role = roles.get(member_name, "villager")
        role_prompt = WEREWOLF_ROLE_PROMPTS.get(role, WEREWOLF_ROLE_PROMPTS["villager"])
        display_name = spec.display_name or member_name

        teammates = ""
        if role == "werewolf":
            wolf_teammates = [m for m in alive_members if roles.get(m) == "werewolf" and m != member_name]
            if wolf_teammates:
                teammate_names = []
                for wt in wolf_teammates:
                    wt_spec = get_model_by_name(wt)
                    teammate_names.append(wt_spec.display_name if wt_spec and wt_spec.display_name else wt)
                teammates = "、".join(teammate_names)

        msgs = _build_werewolf_messages(
            role=role,
            role_prompt=role_prompt,
            history=history,
            phase=phase,
            sub_phase=sub_phase,
            message=message,
            alive_players=alive_display_names,
            teammates=teammates,
        )

        try:
            content = await _run_model_stream(
                websocket,
                member_name,
                msgs,
                "werewolf_stream_token",
                {"display_name": display_name, "role": role, "phase": phase, "sub_phase": sub_phase, "round": game.get("current_round", 1)}
            )
            await websocket.send_json({
                "type": "werewolf_reply",
                "model_name": member_name,
                "display_name": display_name,
                "content": content,
                "role": role,
                "phase": phase,
                "sub_phase": sub_phase,
                "round": game.get("current_round", 1),
            })
        except Exception as exc:
            await websocket.send_json({"type": "error", "message": str(exc)})

    await websocket.send_json({
        "type": "werewolf_phase_complete",
        "phase": phase,
        "sub_phase": sub_phase,
        "round": game.get("current_round", 1),
    })
