from __future__ import annotations

import json
from typing import Any

from arena.config import BENCHMARK_DB, RESULTS_DB


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
