from pathlib import Path

BASE_MODEL_DIR = Path(r"E:\local_LLM\Models_Repo")
APP_TITLE = "Llama.cpp 多模型竞技场 Pro"
DEFAULT_SYSTEM_PROMPT = (
    "你是一名专业、准确、简洁的中文助手。"
    "请优先直接回答用户问题；如果存在不确定性，请明确说明。"
)
RESULTS_DB = Path(r"E:\local_LLM\arena_results.json")
BENCHMARK_DB = Path(r"E:\local_LLM\arena_benchmarks.json")
