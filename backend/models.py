from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.config import BASE_MODEL_DIR
from backend.storage import load_model_configs


@dataclass(frozen=True)
class ModelSpec:
    label: str
    path: str
    relative_path: str
    layers: int = 0
    params: str = ""
    quant: str = ""
    size_gb: float = 0.0
    avatar: str = ""
    system_prompt: str = ""
    display_name: str = ""
    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    repeat_penalty: float | None = None


def parse_model_info(path: Path) -> dict[str, Any]:
    name = path.stem
    info: dict[str, Any] = {"params": "", "quant": "", "layers": 0}
    m = re.search(r"(\d+\.?\d*)[Bb]", name)
    if m:
        info["params"] = m.group(1) + "B"
    m = re.search(r"[Qq](\d+[_\w]+)", name)
    if m:
        info["quant"] = "Q" + m.group(1)
    size_gb = path.stat().st_size / (1024 ** 3)
    info["size_gb"] = round(size_gb, 2)
    return info


def discover_models() -> list[ModelSpec]:
    configs = load_model_configs()
    specs: list[ModelSpec] = []
    if not BASE_MODEL_DIR.exists():
        return specs
    for model_path in sorted(BASE_MODEL_DIR.rglob("*.gguf")):
        if "mmproj" in model_path.name.lower():
            continue
        try:
            relative_path = str(model_path.relative_to(BASE_MODEL_DIR))
        except ValueError:
            relative_path = str(model_path)
        info = parse_model_info(model_path)
        model_name = model_path.stem
        cfg = configs.get(model_name, {})
        display_name = cfg.get("display_name", model_name)
        label = f"{display_name}  |  {model_path.parent.name}"
        specs.append(
            ModelSpec(
                label=label,
                path=str(model_path),
                relative_path=relative_path,
                params=info.get("params", ""),
                quant=info.get("quant", ""),
                size_gb=info.get("size_gb", 0.0),
                avatar=cfg.get("avatar", ""),
                system_prompt=cfg.get("system_prompt", ""),
                display_name=display_name,
                temperature=cfg.get("temperature"),
                max_tokens=cfg.get("max_tokens"),
                top_p=cfg.get("top_p"),
                repeat_penalty=cfg.get("repeat_penalty"),
            )
        )
    return specs


def get_spec_map() -> dict[str, ModelSpec]:
    return {spec.path: spec for spec in discover_models()}


def get_model_by_name(name: str) -> ModelSpec | None:
    for spec in discover_models():
        if Path(spec.path).stem == name:
            return spec
    return None
