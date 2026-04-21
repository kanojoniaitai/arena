from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import gradio as gr

from arena.config import APP_TITLE, DEFAULT_SYSTEM_PROMPT
from arena.engine import run_single_model
from arena.models import discover_models, get_spec_map
from arena.storage import load_results_db, save_results_db
from arena.styles import CUSTOM_CSS
from arena.ui import (
    render_benchmark_table,
    render_leaderboard,
    render_multi_chat,
)
from arena.benchmark import run_benchmark_all

# Discover initial models
initial_specs = discover_models()


def clear_multi_chat():
    return {}, render_multi_chat({}, {}), "历史记录已清空。"


def multi_chat_sequential(
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
    histories: dict[str, list[dict[str, str]]]
):
    prompt = (user_prompt or "").strip()
    if not prompt:
        yield "", histories, render_multi_chat(histories, {}), "请输入你的指令后再开始生成。"
        return
        
    spec_map = get_spec_map()
    ordered_specs = [spec_map[p] for p in selected_model_paths if p in spec_map]
    if not ordered_specs:
        yield prompt, histories, render_multi_chat(histories, {}), "请至少选择一个有效的模型。"
        return

    # Add system prompt if history is empty for a model, then append user message
    for spec in ordered_specs:
        name = Path(spec.path).stem
        if name not in histories:
            histories[name] = [{"role": "system", "content": system_prompt.strip()}]
        histories[name].append({"role": "user", "content": prompt})

    # Initialize statuses
    statuses = {Path(spec.path).stem: {"status": "等待中"} for spec in ordered_specs}
    
    # Yield initial state with user message
    yield "", histories, render_multi_chat(histories, statuses), f"已进入队列，共 {len(ordered_specs)} 个模型，准备顺序执行。"

    results_for_db = []

    for idx, spec in enumerate(ordered_specs):
        name = Path(spec.path).stem
        statuses[name] = {"status": "加载中"}
        yield "", histories, render_multi_chat(histories, statuses), f"正在处理第 {idx + 1}/{len(ordered_specs)} 个模型：{name}"
        
        # Append an empty assistant message to be filled
        histories[name].append({"role": "assistant", "content": ""})
        
        # Pass only the history up to the current turn (excluding the empty assistant message we just appended)
        messages_for_llm = histories[name][:-1]
        
        final_result = None
        for result in run_single_model(
            spec=spec,
            messages=messages_for_llm,
            n_ctx=n_ctx,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=repeat_penalty,
            n_gpu_layers=n_gpu_layers,
            n_batch=n_batch,
            seed=seed,
        ):
            final_result = result
            statuses[name] = result
            # Update the latest assistant message content
            histories[name][-1]["content"] = result.get("answer", "")
            yield "", histories, render_multi_chat(histories, statuses), f"[{name}] {result.get('status')}..."
            
        results_for_db.append({
            "name": name,
            "status": final_result.get("status", "未知"),
            "elapsed": final_result.get("elapsed", ""),
            "tps": final_result.get("tps", 0),
        })
        
    # After all models complete
    completed = [r for r in results_for_db if r["status"] == "已完成"]
    failed = [r for r in results_for_db if r["status"] == "失败"]
    
    best_name = ""
    if completed:
        best = max(completed, key=lambda x: x.get("tps", 0))
        best_name = best["name"]
        if best_name in statuses:
            statuses[best_name]["perf"] += " 🏆"
            
    yield "", histories, render_multi_chat(histories, statuses), f"全部处理结束：成功 {len(completed)} 个，失败 {len(failed)} 个。"

    # Save to DB
    db_entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "models": [r["name"] for r in results_for_db],
        "winner": best_name,
        "prompt": prompt[:200],
        "results": results_for_db,
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
        status_text,
    )


# Toggle views based on Sidebar selection
def change_view(view_name):
    return (
        gr.update(visible=(view_name == "arena")),
        gr.update(visible=(view_name == "leaderboard")),
        gr.update(visible=(view_name == "benchmark"))
    )


with gr.Blocks(title=APP_TITLE, theme=gr.themes.Base()) as demo:
    # State for multi-chat history
    chat_histories = gr.State({})

    with gr.Row():
        # SIDEBAR
        with gr.Column(scale=2, min_width=240, elem_classes="sidebar"):
            gr.HTML(
                """
                <div style="font-size: 20px; font-weight: 700; color: #fafafa; margin-bottom: 24px; display: flex; align-items: center; gap: 12px;">
                    <span style="display: inline-block; width: 12px; height: 12px; background: #3b82f6; border-radius: 50%; box-shadow: 0 0 12px #3b82f6;"></span>
                    Arena Pro
                </div>
                """
            )
            
            nav_radio = gr.Radio(
                choices=[
                    ("⚔️ 对战与聊天", "arena"),
                    ("🏆 历史排行榜", "leaderboard"),
                    ("📊 边界能力测试", "benchmark")
                ],
                value="arena",
                label="导航",
                elem_id="nav-radio"
            )
            
            gr.HTML('<div style="margin-top: 32px; margin-bottom: 12px; font-size: 12px; font-weight: 600; color: #a1a1aa; text-transform: uppercase;">模型设置</div>')
            
            model_selector = gr.CheckboxGroup(
                label="参与对战/聊天的模型",
                choices=[(spec.label, spec.path) for spec in initial_specs],
                value=[spec.path for spec in initial_specs],
            )
            refresh_btn = gr.Button("刷新模型库", variant="secondary", size="sm")
            model_scan_status = gr.Markdown(f"已发现 {len(initial_specs)} 个可用模型。")
            
            gr.HTML('<div style="margin-top: 24px; margin-bottom: 12px; font-size: 12px; font-weight: 600; color: #a1a1aa; text-transform: uppercase;">推理参数</div>')
            
            with gr.Accordion("高级参数", open=False):
                system_prompt = gr.Textbox(label="系统提示词", value=DEFAULT_SYSTEM_PROMPT, lines=3)
                n_ctx = gr.Slider(2048, 32768, value=8192, step=512, label="n_ctx")
                max_tokens = gr.Slider(128, 8192, value=2048, step=128, label="max_tokens")
                n_batch = gr.Slider(64, 2048, value=512, step=64, label="n_batch")
                n_gpu_layers = gr.Slider(-1, 256, value=-1, step=1, label="n_gpu_layers")
                temperature = gr.Slider(0.0, 1.5, value=0.7, step=0.05, label="temperature")
                top_p = gr.Slider(0.1, 1.0, value=0.95, step=0.05, label="top_p")
                repeat_penalty = gr.Slider(1.0, 1.5, value=1.05, step=0.01, label="repeat_penalty")
                seed = gr.Number(value=-1, precision=0, label="seed (-1 为随机)")

        # MAIN CONTENT
        with gr.Column(scale=9):
            
            # VIEW: ARENA (Chat & Compare)
            with gr.Column(visible=True) as view_arena:
                with gr.Group(elem_classes="panel"):
                    gr.HTML('<div class="panel-title">竞技场会话</div>')
                    
                    # Unified Chat Display
                    chat_display = gr.HTML(render_multi_chat({}, {}))
                    
                    with gr.Row():
                        user_prompt = gr.Textbox(
                            show_label=False,
                            placeholder="输入指令，按顺序触发所有选中模型...",
                            lines=3,
                            elem_id="chat-input",
                            scale=8,
                        )
                        send_btn = gr.Button("发送 (顺序生成)", variant="primary", scale=2)
                    
                    with gr.Row():
                        clear_chat_btn = gr.Button("清空上下文记录", variant="secondary")
                        status_box = gr.Textbox(label="运行状态", interactive=False, lines=1)

            # VIEW: LEADERBOARD
            with gr.Column(visible=False) as view_leaderboard:
                with gr.Group(elem_classes="panel"):
                    gr.HTML('<div class="panel-title">历史战绩与速度排行榜</div>')
                    leaderboard_html = gr.HTML(render_leaderboard())
                    refresh_lb_btn = gr.Button("刷新排行榜", variant="secondary")

            # VIEW: BENCHMARK
            with gr.Column(visible=False) as view_benchmark:
                with gr.Group(elem_classes="panel"):
                    gr.HTML('<div class="panel-title">边界能力检测</div>')
                    gr.Markdown("注意：基准测试将独占执行，依次对选中的模型进行极限上下文、吞吐量、大海捞针及各项边界能力测试。")
                    with gr.Row():
                        run_bench_btn = gr.Button("开始基准测试", variant="primary")
                        refresh_bench_btn = gr.Button("刷新表格", variant="secondary")
                    bench_status = gr.Textbox(label="测试状态", interactive=False)
                    benchmark_table = gr.HTML(render_benchmark_table())

    # Wiring
    nav_radio.change(
        fn=change_view,
        inputs=[nav_radio],
        outputs=[view_arena, view_leaderboard, view_benchmark]
    )

    send_btn.click(
        fn=multi_chat_sequential,
        inputs=[
            model_selector, user_prompt, system_prompt, n_ctx, max_tokens,
            temperature, top_p, repeat_penalty, n_gpu_layers, n_batch, seed, chat_histories
        ],
        outputs=[user_prompt, chat_histories, chat_display, status_box],
    )
    
    clear_chat_btn.click(
        fn=clear_multi_chat,
        inputs=None,
        outputs=[chat_histories, chat_display, status_box],
    )

    refresh_btn.click(
        fn=refresh_model_choices,
        inputs=None,
        outputs=[model_selector, model_scan_status],
    )

    refresh_lb_btn.click(
        fn=lambda: render_leaderboard(),
        inputs=None,
        outputs=[leaderboard_html],
    )

    run_bench_btn.click(
        fn=run_benchmark_all,
        inputs=[model_selector],
        outputs=[benchmark_table, bench_status],
    )
    refresh_bench_btn.click(
        fn=lambda: render_benchmark_table(),
        inputs=None,
        outputs=[benchmark_table],
    )

demo.queue(default_concurrency_limit=1)

if __name__ == "__main__":
    print(f"正在启动 {APP_TITLE} ...")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7866,
        share=False,
        css=CUSTOM_CSS,
    )