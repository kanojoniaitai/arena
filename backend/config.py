import os
from pathlib import Path

BASE_MODEL_DIR = Path(os.environ.get("BASE_MODEL_DIR", r"E:\local_LLM\Models_Repo"))
APP_TITLE = "Llama.cpp 多模型竞技场 Pro"
DEFAULT_SYSTEM_PROMPT = (
    "你是一名专业、准确、简洁的中文助手。"
    "请优先直接回答用户问题；如果存在不确定性，请明确说明。"
)
RESULTS_DB = Path(r"arena_results.json")
BENCHMARK_DB = Path(r"arena_benchmarks.json")
STATIC_DIR = Path(__file__).parent / "static"
MODEL_CONFIGS_DB = Path(r"arena_model_configs.json")
GROUPS_DB = Path(r"arena_groups.json")
CHAT_HISTORY_DB = Path(r"arena_chat_history.json")
LLM_PARAMS = {
    "n_ctx": 8192,
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.95,
    "repeat_penalty": 1.05,
    "n_gpu_layers": -1,
    "n_batch": 512,
    "seed": -1,
}
