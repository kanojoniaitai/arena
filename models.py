from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config import BASE_MODEL_DIR


@dataclass(frozen=True)
class ModelSpec:
    label: str
    path: str
    relative_path: str
    layers: int = 0
    params: str = ""
    quant: str = ""
    size_gb: float = 0.0


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
        label = f"{model_path.stem}  |  {model_path.parent.name}"
        specs.append(
            ModelSpec(
                label=label,
                path=str(model_path),
                relative_path=relative_path,
                params=info.get("params", ""),
                quant=info.get("quant", ""),
                size_gb=info.get("size_gb", 0.0),
            )
        )
    return specs


def get_spec_map() -> dict[str, ModelSpec]:
    return {spec.path: spec for spec in discover_models()}
