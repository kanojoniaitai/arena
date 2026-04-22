from __future__ import annotations

import gc
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from llama_cpp import Llama

from models import ModelSpec
from storage import load_benchmark_db, save_benchmark_db


@dataclass
class BenchmarkResult:
    model_name: str
    vram_mb: float = 0.0
    max_context: int = 0
    prefill_512: float = 0.0
    prefill_2k: float = 0.0
    decode_512: float = 0.0
    ttft_ms: float = 0.0
    needle_pass: bool = False
    logprob: float = 0.0
    json_adherence: bool = False
    math_logic: bool = False
    multilingual: bool = False
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))


def run_benchmark_single(name: str, path: str, progress_cb: Callable[[str], None]) -> BenchmarkResult:
    res = BenchmarkResult(model_name=name)
    try:
        progress_cb(f"[{name}] 加载模型并检测层数/VRAM...")
        llm = Llama(model_path=path, n_gpu_layers=-1, n_ctx=4096, verbose=False, n_batch=512)
        info = llm.metadata
        res.layers = int(info.get("llama.block_count") or info.get("n_layer") or 0)
        llm.close()
        gc.collect()

        progress_cb(f"[{name}] 测试极限上下文...")
        contexts = [4096, 8192, 16384, 24576, 32768]
        max_ctx = 4096
        for ctx in contexts:
            try:
                llm = Llama(model_path=path, n_gpu_layers=-1, n_ctx=ctx, verbose=False, n_batch=512)
                llm.close()
                gc.collect()
                max_ctx = ctx
            except Exception:
                break
        res.max_context = max_ctx

        progress_cb(f"[{name}] 测试吞吐量...")
        llm = Llama(model_path=path, n_gpu_layers=-1, n_ctx=8192, verbose=False, n_batch=512)
        text_512 = " ".join(["benchmark"] * 256)
        t0 = time.perf_counter()
        llm.create_completion(prompt=text_512, max_tokens=1, temperature=0.0)
        res.prefill_512 = round(512 / (time.perf_counter() - t0), 2)

        text_2k = " ".join(["benchmark"] * 1024)
        t0 = time.perf_counter()
        llm.create_completion(prompt=text_2k, max_tokens=1, temperature=0.0)
        res.prefill_2k = round(2048 / (time.perf_counter() - t0), 2)

        t0 = time.perf_counter()
        llm.create_completion(prompt="Once upon a time", max_tokens=512, temperature=0.0)
        res.decode_512 = round(512 / (time.perf_counter() - t0), 2)

        res.ttft_ms = round((512 / res.prefill_512) * 1000, 1) if res.prefill_512 else 0.0

        progress_cb(f"[{name}] 大海捞针测试...")
        secret = "服务器密码是：K9X2@pL"
        question = "文中提到的服务器密码是什么？请准确复述。"
        filler = "在遥远的未来，人类已经掌握了星际旅行的技术。宇宙飞船穿梭于各个星系之间，探索未知的星球。"
        filler_tokens = llm.tokenize(filler.encode("utf-8"))
        repeats = (max_ctx - 200) // len(filler_tokens) if filler_tokens else 100
        long_text = (filler + "\n") * repeats
        parts = long_text.split("\n")
        third = len(parts) // 3
        parts.insert(0, secret)
        parts.insert(third + 1, secret)
        parts.append(secret)
        haystack = "\n".join(parts)
        prompt = haystack + "\n\n" + question
        try:
            out = llm.create_completion(prompt=prompt, max_tokens=64, temperature=0.0, stop=["\n"])
            answer = out["choices"][0]["text"].strip()
            res.needle_pass = secret in answer
        except Exception:
            res.needle_pass = False

        progress_cb(f"[{name}] 测试续写置信度...")
        test_prompt = (
            "Artificial intelligence (AI) is the intelligence of machines or software, "
            "as opposed to the intelligence of humans or animals. It is a field of study in computer science.\n"
        )
        try:
            llm_log = Llama(model_path=path, n_gpu_layers=-1, n_ctx=2048, verbose=False, n_batch=512, logits_all=True)
            out = llm_log.create_completion(prompt=test_prompt, max_tokens=1, temperature=0.0, logprobs=1)
            logprobs = out["choices"][0].get("logprobs", {})
            lp = logprobs.get("token_logprobs", [None])[0]
            res.logprob = float(lp) if lp is not None else 0.0
            llm_log.close()
        except Exception:
            res.logprob = 0.0

        progress_cb(f"[{name}] 测试 JSON 遵循度...")
        try:
            json_prompt = "User: Return a JSON object with keys 'name' (string) and 'age' (int) for a 30 year old named Alice. ONLY return valid JSON, no other text.\nAssistant: "
            out = llm.create_completion(prompt=json_prompt, max_tokens=128, temperature=0.0)
            answer = out["choices"][0]["text"].strip()
            res.json_adherence = '{"name"' in answer.replace(" ", "") and "30" in answer
        except Exception:
            res.json_adherence = False

        progress_cb(f"[{name}] 测试多语言混合边界...")
        try:
            multi_prompt = "User: Translate 'Apple' to French, Japanese, and Emoji. Format: fr:X, jp:Y, emoji:Z\nAssistant: "
            out = llm.create_completion(prompt=multi_prompt, max_tokens=64, temperature=0.0)
            answer = out["choices"][0]["text"].strip().lower()
            res.multilingual = "pomme" in answer and ("りんご" in answer or "リンゴ" in answer) and "🍎" in answer
        except Exception:
            res.multilingual = False

        progress_cb(f"[{name}] 测试逻辑推理边界...")
        try:
            math_prompt = "User: If x = 5 and y = x * 3 - 2, what is x + y? Answer with just the number.\nAssistant: "
            out = llm.create_completion(prompt=math_prompt, max_tokens=16, temperature=0.0)
            answer = out["choices"][0]["text"].strip()
            res.math_logic = "18" in answer
        except Exception:
            res.math_logic = False

        llm.close()
        gc.collect()
        progress_cb(f"[{name}] 完成！")
    except Exception as e:
        progress_cb(f"[{name}] 失败: {e}")
    return res


def run_benchmark_all(selected_model_paths: list[str]):
    from models import get_spec_map
    spec_map = get_spec_map()
    specs = [spec_map[p] for p in selected_model_paths if p in spec_map]
    if not specs:
        yield "", "请至少选择一个模型进行基准测试。"
        return

    status_lines: list[str] = []
    db = load_benchmark_db()

    def cb(msg: str):
        status_lines.append(msg)

    from ui import render_benchmark_table
    for spec in specs:
        yield render_benchmark_table(), "\n".join(status_lines[-10:])
        res = run_benchmark_single(spec.label, spec.path, cb)
        db[Path(spec.path).stem] = {
            "vram_mb": res.vram_mb,
            "max_context": res.max_context,
            "prefill_512": res.prefill_512,
            "prefill_2k": res.prefill_2k,
            "decode_512": res.decode_512,
            "ttft_ms": res.ttft_ms,
            "needle_pass": res.needle_pass,
            "logprob": res.logprob,
            "json_adherence": res.json_adherence,
            "math_logic": res.math_logic,
            "multilingual": res.multilingual,
            "timestamp": res.timestamp,
        }
        save_benchmark_db(db)
        yield render_benchmark_table(), "\n".join(status_lines[-10:])

    yield render_benchmark_table(), "全部基准测试完成！数据已保存。"
