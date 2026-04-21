from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import gradio as gr

from arena.chat_session import ChatSession
from arena.config import APP_TITLE, DEFAULT_SYSTEM_PROMPT
from arena.engine import run_single_model
from arena.models import discover_models, get_spec_map
from arena.storage import load_results_db, save_results_db
from arena.styles import CUSTOM_CSS
from arena.ui import (
    render_benchmark_table,
    render_chat_history,
    render_leaderboard,
    render_model_gallery,
    render_result_cards,
)


def compare_models_sequential(
    selected_model_paths: list[str],
    user_prompt: str,
    system_prompt: str,
    n_ctx: int,
    max_tokens: int,
    temperature: float,
    top_p: float,
    repeat_penalty: float,
    n_gpu_layers: int,
    n_batch: int,
    seed: int,
):
    prompt = (user_prompt or "").strip()
    system_prompt = (system_prompt or DEFAULT_SYSTEM_PROMPT).strip()
    spec_map = get_spec_map()
    if not prompt:
        yield render_result_cards([]), "请输入你的指令后再开始对比。"
        return
    if not selected_model_paths:
        yield render_result_cards([]), "请至少选择一个模型。"
        return
    ordered_specs: list[Any] = []
    for model_path in selected_model_paths:
        if model_path in spec_map:
            ordered_specs.append(spec_map[model_path])
    if not ordered_specs:
        yield render_result_cards([]), "当前选择的模型无效，请先刷新模型列表。"
        return

    results: list[dict[str, Any]] = []
    for spec in ordered_specs:
        results.append(
            {
                "name": Path(spec.path).stem,
                "path": spec.relative_path,
                "status": "等待中",
                "detail": "等待调度。",
                "answer": "",
                "elapsed": "",
                "perf": "",
            }
        )

    yield render_result_cards(results), f"已进入队列，共 {len(ordered_specs)} 个模型，准备顺序执行。"

    for idx, spec in enumerate(ordered_specs):
        results[idx]["status"] = "加载中"
        results[idx]["detail"] = "顺序加载中..."
        yield render_result_cards(results), f"正在处理第 {idx + 1}/{len(ordered_specs)} 个模型：{Path(spec.path).stem}"
        run_single_model(
            spec, prompt, system_prompt, n_ctx, max_tokens,
            temperature, top_p, repeat_penalty, n_gpu_layers,
            n_batch, seed, results[idx]
        )
        yield render_result_cards(results), f"{Path(spec.path).stem} 已完成。"

    completed = [r for r in results if r["status"] == "已完成"]
    failed = [r for r in results if r["status"] == "失败"]

    if completed:
        best = max(completed, key=lambda x: x.get("tps", 0))
        for r in results:
            if r["name"] == best["name"]:
                r["detail"] += " 🏆 速度之王"

    yield render_result_cards(results), f"全部处理结束：成功 {len(completed)} 个，失败 {len(failed)} 个。"

    db_entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "models": [r["name"] for r in results],
        "winner": best["name"] if completed else "",
        "prompt": prompt[:200],
        "results": [
            {
                "name": r["name"],
                "status": r["status"],
                "elapsed": r.get("elapsed", ""),
                "tps": r.get("tps", 0),
            }
            for r in results
        ],
    }
    db = load_results_db()
    db.append(db_entry)
    save_results_db(db)


def refresh_model_choices():
    specs = discover_models()
    choices = [(spec.label, spec.path) for spec in specs]
    default_values = [spec.path for spec in specs]
    status_text = f"已发现 {len(specs)} 个可用 GGUF 模型。"
    return (
        gr.update(choices=choices, value=default_values),
        render_model_gallery(specs),
        status_text,
    )


def clear_results():
    return "", render_result_cards([]), "已清空输出。"


# Global chat session manager
_chat_session = ChatSession()


def chat_load_model(model_path: str, n_ctx: int, n_gpu_layers: int, n_batch: int) -> tuple[str, str]:
    spec_map = get_spec_map()
    if model_path not in spec_map:
        return render_chat_history("", {"name": "未选择", "loaded": False}), "模型路径无效"
    spec = spec_map[model_path]
    _chat_session.n_ctx = n_ctx
    _chat_session.n_gpu_layers = n_gpu_layers
    _chat_session.n_batch = n_batch
    ok = _chat_session.load_model(spec)
    info = _chat_session.get_model_info()
    history = _chat_session.get_history_text()
    if ok:
        return render_chat_history(history, info), f"已加载：{spec.label}"
    return render_chat_history(history, info), f"加载失败：{_chat_session.load_error}"


def chat_send_message(user_input: str, max_tokens: int, temperature: float, top_p: float, repeat_penalty: float, seed: int) -> tuple[str, str]:
    if not _chat_session.llm:
        info = _chat_session.get_model_info()
        history = _chat_session.get_history_text()
        return render_chat_history(history, info), "请先加载模型"
    if not user_input.strip():
        info = _chat_session.get_model_info()
        history = _chat_session.get_history_text()
        return render_chat_history(history, info), "输入为空"
    _chat_session.temperature = temperature
    _chat_session.top_p = top_p
    _chat_session.repeat_penalty = repeat_penalty
    response = _chat_session.generate_response(user_input.strip(), max_tokens=max_tokens, seed=seed)
    info = _chat_session.get_model_info()
    history = _chat_session.get_history_text()
    return render_chat_history(history, info), ""


def chat_clear_history() -> tuple[str, str]:
    _chat_session.clear_history()
    info = _chat_session.get_model_info()
    return render_chat_history("", info), "历史已清空"


def chat_set_system(system_prompt: str) -> str:
    _chat_session.set_system_prompt(system_prompt)
    return "系统提示词已更新"


initial_specs = discover_models()

with gr.Blocks(title=APP_TITLE) as demo:
    gr.HTML(
        """
        <div class="app-shell">
          <div class="hero">
            <div class="hero-title">Llama.cpp 多模型竞技场 Pro</div>
            <div class="hero-subtitle">
              自动扫描 <b>E:\\local_LLM\\Models_Repo</b> 下的 GGUF 模型，
              支持<b>顺序对战</b>、<b>速度排行榜</b>、<b>边界能力基准测试</b>、<b>单模型聊天</b>。
            </div>
          </div>
        </div>
        """
    )

    with gr.Tabs():
        with gr.TabItem("对战竞技场"):
            with gr.Row():
                with gr.Column(scale=4):
                    with gr.Group(elem_classes="panel"):
                        gr.HTML('<div class="panel-title">Prompt Studio</div>')
                        user_prompt = gr.Textbox(
                            label="你的指令",
                            lines=7,
                            placeholder="例如：请从产品经理视角，写一份本地知识库问答系统的 MVP 方案。",
                            elem_id="prompt-box",
                        )
                        system_prompt = gr.Textbox(
                            label="系统提示词",
                            value=DEFAULT_SYSTEM_PROMPT,
                            lines=4,
                            elem_id="system-box",
                        )
                        with gr.Row():
                            run_seq_btn = gr.Button("开始顺序对比", variant="primary")
                            clear_btn = gr.Button("清空结果", variant="secondary")

                with gr.Column(scale=3):
                    with gr.Group(elem_classes="panel"):
                        gr.HTML('<div class="panel-title">模型选择</div>')
                        model_selector = gr.CheckboxGroup(
                            label="已发现的聊天模型",
                            choices=[(spec.label, spec.path) for spec in initial_specs],
                            value=[spec.path for spec in initial_specs],
                        )
                        with gr.Row():
                            refresh_btn = gr.Button("刷新模型库", variant="secondary")
                        model_scan_status = gr.Markdown(
                            f"已发现 {len(initial_specs)} 个可用 GGUF 模型。"
                        )

            with gr.Row():
                with gr.Column(scale=3):
                    with gr.Group(elem_classes="panel"):
                        gr.HTML('<div class="panel-title">推理参数</div>')
                        n_ctx = gr.Slider(2048, 32768, value=8192, step=512, label="n_ctx")
                        max_tokens = gr.Slider(128, 8192, value=2048, step=128, label="max_tokens")
                        n_batch = gr.Slider(64, 2048, value=512, step=64, label="n_batch")
                        n_gpu_layers = gr.Slider(-1, 256, value=-1, step=1, label="n_gpu_layers")
                        temperature = gr.Slider(0.0, 1.5, value=0.7, step=0.05, label="temperature")
                        top_p = gr.Slider(0.1, 1.0, value=0.95, step=0.05, label="top_p")
                        repeat_penalty = gr.Slider(1.0, 1.5, value=1.05, step=0.01, label="repeat_penalty")
                        seed = gr.Number(value=-1, precision=0, label="seed (-1 为随机)")

                with gr.Column(scale=5):
                    with gr.Group(elem_classes="panel"):
                        gr.HTML('<div class="panel-title">模型展厅</div>')
                        gr.HTML(
                            """
                            <div>
                              <span class="stat-chip">顺序加载，减少显存占用</span>
                              <span class="stat-chip">自动记录速度与历史战绩</span>
                              <span class="stat-chip">自动跳过 mmproj 文件</span>
                            </div>
                            """
                        )
                        model_gallery = gr.HTML(render_model_gallery(initial_specs))

            with gr.Row():
                with gr.Column(scale=8):
                    with gr.Group(elem_classes="panel"):
                        gr.HTML('<div class="panel-title">结果面板</div>')
                        result_cards = gr.HTML(render_result_cards([]))
                with gr.Column(scale=3):
                    with gr.Group(elem_classes="panel"):
                        gr.HTML('<div class="panel-title">运行状态</div>')
                        status_box = gr.Textbox(
                            label="状态",
                            value="等待开始。",
                            lines=10,
                            interactive=False,
                            elem_id="status-box",
                        )

        with gr.TabItem("历史排行榜"):
            with gr.Group(elem_classes="panel"):
                gr.HTML('<div class="panel-title">对战历史 & 速度排行榜</div>')
                leaderboard_html = gr.HTML(render_leaderboard())
                refresh_lb_btn = gr.Button("刷新排行榜", variant="secondary")

        with gr.TabItem("边界能力检测"):
            with gr.Row():
                with gr.Column(scale=3):
                    with gr.Group(elem_classes="panel"):
                        gr.HTML('<div class="panel-title">选择待测模型</div>')
                        bench_model_selector = gr.CheckboxGroup(
                            label="模型",
                            choices=[(spec.label, spec.path) for spec in initial_specs],
                            value=[spec.path for spec in initial_specs],
                        )
                        run_bench_btn = gr.Button("运行边界能力检测", variant="primary")
                        bench_status = gr.Textbox(label="测试状态", lines=8, interactive=False)
                with gr.Column(scale=7):
                    with gr.Group(elem_classes="panel"):
                        gr.HTML('<div class="panel-title">基准测试数据</div>')
                        benchmark_table = gr.HTML(render_benchmark_table())
                        refresh_bench_btn = gr.Button("刷新表格", variant="secondary")

        with gr.TabItem("聊天模式"):
            with gr.Row():
                with gr.Column(scale=3):
                    with gr.Group(elem_classes="panel"):
                        gr.HTML('<div class="panel-title">模型控制</div>')
                        chat_model_dropdown = gr.Dropdown(
                            label="选择模型",
                            choices=[(spec.label, spec.path) for spec in initial_specs],
                            value=initial_specs[0].path if initial_specs else None,
                        )
                        chat_n_ctx = gr.Slider(2048, 32768, value=8192, step=512, label="n_ctx")
                        chat_n_gpu = gr.Slider(-1, 256, value=-1, step=1, label="n_gpu_layers")
                        chat_n_batch = gr.Slider(64, 2048, value=512, step=64, label="n_batch")
                        chat_load_btn = gr.Button("加载模型", variant="primary")
                        chat_model_status = gr.Textbox(label="加载状态", interactive=False)

                    with gr.Group(elem_classes="panel"):
                        gr.HTML('<div class="panel-title">聊天参数</div>')
                        chat_system = gr.Textbox(
                            label="系统提示词",
                            value=DEFAULT_SYSTEM_PROMPT,
                            lines=3,
                        )
                        chat_max_tokens = gr.Slider(128, 4096, value=1024, step=128, label="max_tokens")
                        chat_temperature = gr.Slider(0.0, 1.5, value=0.7, step=0.05, label="temperature")
                        chat_top_p = gr.Slider(0.1, 1.0, value=0.95, step=0.05, label="top_p")
                        chat_repeat = gr.Slider(1.0, 1.5, value=1.05, step=0.01, label="repeat_penalty")
                        chat_seed = gr.Number(value=-1, precision=0, label="seed")
                        chat_apply_sys_btn = gr.Button("应用系统提示词", variant="secondary")
                        chat_sys_status = gr.Textbox(label="", interactive=False)

                with gr.Column(scale=5):
                    with gr.Group(elem_classes="panel"):
                        gr.HTML('<div class="panel-title">对话窗口</div>')
                        chat_display = gr.HTML(render_chat_history("", {"name": "未选择", "loaded": False}))
                        with gr.Row():
                            chat_input = gr.Textbox(
                                label="输入消息",
                                lines=2,
                                elem_id="chat-input",
                                scale=4,
                            )
                            chat_send_btn = gr.Button("发送", variant="primary", scale=1)
                        chat_clear_btn = gr.Button("清空历史", variant="secondary")
                        chat_response_status = gr.Textbox(label="", interactive=False)

    run_seq_btn.click(
        fn=compare_models_sequential,
        inputs=[
            model_selector, user_prompt, system_prompt, n_ctx, max_tokens,
            temperature, top_p, repeat_penalty, n_gpu_layers, n_batch, seed,
        ],
        outputs=[result_cards, status_box],
    )
    clear_btn.click(
        fn=clear_results,
        inputs=None,
        outputs=[user_prompt, result_cards, status_box],
    )
    refresh_btn.click(
        fn=refresh_model_choices,
        inputs=None,
        outputs=[model_selector, model_gallery, model_scan_status],
    )
    refresh_lb_btn.click(
        fn=lambda: render_leaderboard(),
        inputs=None,
        outputs=[leaderboard_html],
    )

    from arena.benchmark import run_benchmark_all
    run_bench_btn.click(
        fn=run_benchmark_all,
        inputs=[bench_model_selector],
        outputs=[benchmark_table, bench_status],
    )
    refresh_bench_btn.click(
        fn=lambda: render_benchmark_table(),
        inputs=None,
        outputs=[benchmark_table],
    )

    chat_load_btn.click(
        fn=chat_load_model,
        inputs=[chat_model_dropdown, chat_n_ctx, chat_n_gpu, chat_n_batch],
        outputs=[chat_display, chat_model_status],
    )
    chat_send_btn.click(
        fn=chat_send_message,
        inputs=[chat_input, chat_max_tokens, chat_temperature, chat_top_p, chat_repeat, chat_seed],
        outputs=[chat_display, chat_response_status],
    )
    chat_clear_btn.click(
        fn=chat_clear_history,
        inputs=None,
        outputs=[chat_display, chat_response_status],
    )
    chat_apply_sys_btn.click(
        fn=chat_set_system,
        inputs=[chat_system],
        outputs=[chat_sys_status],
    )

demo.queue(default_concurrency_limit=1)

if __name__ == "__main__":
    print(f"正在启动 {APP_TITLE} ...")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7866,
        share=False,
        theme=gr.themes.Soft(),
        css=CUSTOM_CSS,
    )
