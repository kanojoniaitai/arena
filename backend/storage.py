from __future__ import annotations

import json
from typing import Any

from backend.config import BENCHMARK_DB, CHAT_HISTORY_DB, GROUPS_DB, MODEL_CONFIGS_DB, RESULTS_DB, DEBATES_DB, STORIES_DB, UNDERCOVERS_DB, WEREWOLVES_DB


def load_results_db() -> list[dict[str, Any]]:
    if RESULTS_DB.exists():
        try:
            with open(RESULTS_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_results_db(data: list[dict[str, Any]]) -> None:
    with open(RESULTS_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_benchmark_db() -> dict[str, Any]:
    if BENCHMARK_DB.exists():
        try:
            with open(BENCHMARK_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_benchmark_db(data: dict[str, Any]) -> None:
    with open(BENCHMARK_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_model_configs() -> dict[str, dict[str, str]]:
    if MODEL_CONFIGS_DB.exists():
        try:
            with open(MODEL_CONFIGS_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_model_configs(configs: dict) -> None:
    with open(MODEL_CONFIGS_DB, "w", encoding="utf-8") as f:
        json.dump(configs, f, ensure_ascii=False, indent=2)


def load_groups() -> list[dict]:
    if GROUPS_DB.exists():
        try:
            with open(GROUPS_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_groups(groups: list[dict]) -> None:
    with open(GROUPS_DB, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)


def load_chat_history() -> dict[str, list[dict]]:
    if CHAT_HISTORY_DB.exists():
        try:
            with open(CHAT_HISTORY_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_chat_history(history: dict[str, list[dict]]) -> None:
    with open(CHAT_HISTORY_DB, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_debates() -> list[dict]:
    if DEBATES_DB.exists():
        try:
            with open(DEBATES_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_debates(debates: list[dict]) -> None:
    with open(DEBATES_DB, "w", encoding="utf-8") as f:
        json.dump(debates, f, ensure_ascii=False, indent=2)


def load_stories() -> list[dict]:
    if STORIES_DB.exists():
        try:
            with open(STORIES_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_stories(stories: list[dict]) -> None:
    with open(STORIES_DB, "w", encoding="utf-8") as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)


def load_undercovers() -> list[dict]:
    if UNDERCOVERS_DB.exists():
        try:
            with open(UNDERCOVERS_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_undercovers(undercovers: list[dict]) -> None:
    with open(UNDERCOVERS_DB, "w", encoding="utf-8") as f:
        json.dump(undercovers, f, ensure_ascii=False, indent=2)


def load_werewolves() -> list[dict]:
    if WEREWOLVES_DB.exists():
        try:
            with open(WEREWOLVES_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_werewolves(werewolves: list[dict]) -> None:
    with open(WEREWOLVES_DB, "w", encoding="utf-8") as f:
        json.dump(werewolves, f, ensure_ascii=False, indent=2)
