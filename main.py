from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import gradio as gr

from config import APP_TITLE, DEFAULT_SYSTEM_PROMPT
from engine import run_single_model
from models import discover_models, get_spec_map
from storage import load_results_db, save_results_db
from styles import CUSTOM_CSS
from ui import (
    render_benchmark_table,
    render_leaderboard,
    render_multi_chat,
    render_single_chat,
    render_stats_dashboard,
    render_export_button,
    render_comparison,
    render_header_html,
    render_model_cards,
    render_sidebar_nav_js,
    render_auto_scroll_js,
    render_prompt_templates,
)
from benchmark import run_benchmark_all

# Discover initial models
initial_specs = discover_models()


def clear_multi_chat():
    return {}, [], "", "", "🧹 历史记录已清空~"


def update_chat_display(histories: dict[str, list[dict[str, str]]]):
    """Format histories into Gradio Chatbot format (list of [user, bot] pairs)"""
    chat_pairs = []
    # Collect all messages chronologically across models, or group by model?
    # For a unified Chatbot, we need a single list of messages.
    # We will format bot messages with model names.
    
    # We need to construct a sequence of user -> [bot1, bot2...] pairs.
    # Since Gradio Chatbot expects [user_msg, bot_msg] pairs, and we have multiple bots,
    # we can concatenate bot responses for the same user prompt, or yield multiple pairs.
    
    # Simple approach: rebuild from histories assuming synchronized turns
    if not histories:
        return []
        
    models = list(histories.keys())
    if not models:
        return []
        
    num_messages = len(histories[models[0]])
    for i in range(num_messages):
        msg = histories[models[0]][i]
        if msg["role"] == "system":
            continue
        elif msg["role"] == "user":
            user_text = msg["content"]
            bot_text_parts = []
            
            # Find the corresponding assistant messages in the next index (i+1)
            if i + 1 < num_messages:
                for m in models:
                    if i + 1 < len(histories[m]) and histories[m][i+1]["role"] == "assistant":
                        ans = histories[m][i+1]["content"]
                        bot_text_parts.append(f"**🤖 {m}**:\n{ans}")
            
            bot_text = "\n\n---\n\n".join(bot_text_parts) if bot_text_parts else "..."
            chat_pairs.append([user_text, bot_text])
            
    return chat_pairs


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
        yield "", histories, update_chat_display(histories), "", "", "⚠️ 请输入你的指令后再开始生成~"
        return

    if not selected_model_paths:
        yield "", histories, update_chat_display(histories), "", "", "⚠️ 请至少选择一个模型~"
        return

    spec_map = get_spec_map()
    ordered_specs = [spec_map[p] for p in selected_model_paths if p in spec_map]
    if not ordered_specs:
        yield "", histories, update_chat_display(histories), "", "", "⚠️ 请至少选择一个有效的模型~"
        return

    for spec in ordered_specs:
        name = Path(spec.path).stem
        if name not in histories:
            histories[name] = [{"role": "system", "content": system_prompt.strip()}]
        histories[name].append({"role": "user", "content": prompt})

    statuses = {Path(spec.path).stem: {"status": "等待中"} for spec in ordered_specs}

    yield "", histories, update_chat_display(histories), render_stats_dashboard(histories, statuses), render_export_button(histories), f"🎯 已进入队列，共 {len(ordered_specs)} 个模型，准备顺序执行~"

    results_for_db = []

    for idx, spec in enumerate(ordered_specs):
        name = Path(spec.path).stem
        statuses[name] = {"status": "加载中"}
        yield "", histories, update_chat_display(histories), render_stats_dashboard(histories, statuses), render_export_button(histories), f"📦 正在处理第 {idx + 1}/{len(ordered_specs)} 个模型：{name}"

        histories[name].append({"role": "assistant", "content": ""})
        messages_for_llm = histories[name][:-1]

        final_result = None
        try:
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
                histories[name][-1]["content"] = result.get("answer", "")
                yield "", histories, update_chat_display(histories), render_stats_dashboard(histories, statuses), render_export_button(histories), f"[{name}] {result.get('status')}..."
        except Exception as exc:
            total_elapsed = 0
            final_result = {"status": "失败", "detail": f"运行异常：{exc}", "elapsed": f"{total_elapsed:.1f}s", "tps": 0, "answer": histories[name][-1]["content"]}
            statuses[name] = final_result

        if final_result is None:
            final_result = {"status": "失败", "detail": "未知错误", "elapsed": "-", "tps": 0}

        results_for_db.append({
            "name": name,
            "status": final_result.get("status", "未知"),
            "elapsed": final_result.get("elapsed", ""),
            "tps": final_result.get("tps", 0),
        })

    completed = [r for r in results_for_db if r["status"] == "已完成"]
    failed = [r for r in results_for_db if r["status"] == "失败"]

    best_name = ""
    if completed:
        best = max(completed, key=lambda x: x.get("tps", 0))
        best_name = best["name"]
        if best_name in statuses:
            statuses[best_name]["perf"] += " 🏆"

    comparison_html = render_comparison(histories, statuses)

    yield "", histories, update_chat_display(histories), render_stats_dashboard(histories, statuses) + comparison_html, render_export_button(histories), f"🎉 全部处理结束：✅ 成功 {len(completed)} 个，❌ 失败 {len(failed)} 个~"

    db_entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "models": [r["name"] for r in results_for_db],
        "winner": best_name,
        "prompt": prompt[:200],
        "results": results_for_db,
    }
    try:
        db = load_results_db()
        db.append(db_entry)
        save_results_db(db)
    except Exception:
        pass


def single_chat_stream(
    model_path: str,
    user_input: str,
    system_prompt: str,
    n_ctx: int,
    max_tokens: int,
    temperature: float,
    top_p: float,
    repeat_penalty: float,
    n_gpu_layers: int,
    n_batch: int,
    seed: int,
    messages: list[dict[str, str]],
):
    user_input = (user_input or "").strip()
    if not user_input:
        yield messages, render_single_chat(messages, "未选择", ""), "⚠️ 请输入消息~"
        return

    if not model_path:
        yield messages, render_single_chat(messages, "未选择", ""), "⚠️ 请先选择一个模型~"
        return

    spec_map = get_spec_map()
    spec = spec_map.get(model_path)
    if not spec:
        yield messages, render_single_chat(messages, "未选择", ""), "⚠️ 请选择一个有效的模型~"
        return

    if not messages:
        messages = [{"role": "system", "content": system_prompt.strip()}]

    messages.append({"role": "user", "content": user_input})
    messages.append({"role": "assistant", "content": ""})

    model_name = Path(spec.path).stem
    yield messages, render_single_chat(messages, model_name, "加载中"), "📦 正在加载模型..."

    final_result = None
    try:
        for result in run_single_model(
            spec=spec,
            messages=messages[:-1],
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
            messages[-1]["content"] = result.get("answer", "")
            yield messages, render_single_chat(messages, model_name, result.get("status", ""), result.get("perf", "")), f"[{model_name}] {result.get('status')}..."
    except Exception as exc:
        final_result = {"status": "失败", "detail": f"运行异常：{exc}", "tps": 0, "perf": ""}

    if final_result:
        yield messages, render_single_chat(messages, model_name, "已完成", final_result.get("perf", "")), f"🎉 完成！{final_result.get('perf', '')}"
    else:
        yield messages, render_single_chat(messages, model_name, "失败", ""), "❌ 运行失败"


def clear_single_chat():
    return [], render_single_chat([], "未选择", ""), "🧹 对话已清空~"


def refresh_model_choices():
    specs = discover_models()
    choices = [(spec.label, spec.path) for spec in specs]
    default_values = [spec.path for spec in specs]
    status_text = f"🔍 已发现 **{len(specs)}** 个可用 GGUF 模型"
    model_cards = render_model_cards(specs)
    return (
        gr.update(choices=choices, value=default_values),
        gr.update(choices=choices, value=choices[0][1] if choices else None),
        status_text,
        model_cards,
    )


def change_view(view_name):
    is_arena = view_name == "arena"
    is_single = view_name == "single"
    is_leaderboard = view_name == "leaderboard"
    is_benchmark = view_name == "benchmark"
    is_models = view_name == "models"
    return (
        gr.update(visible=is_arena),
        gr.update(visible=is_single),
        gr.update(visible=is_leaderboard),
        gr.update(visible=is_benchmark),
        gr.update(visible=is_models),
        gr.update(visible=is_arena),
        gr.update(visible=is_single),
    )


with gr.Blocks(
    title=APP_TITLE,
    theme=gr.themes.Base(
        primary_hue="blue",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Noto Sans SC"),
        font_mono=gr.themes.GoogleFont("Fira Code"),
    ),
    css=CUSTOM_CSS,
) as demo:
    chat_histories = gr.State({})
    single_messages = gr.State([])

    gr.HTML(render_header_html())

    with gr.Row(elem_classes="app-body"):
        with gr.Column(scale=0, min_width=280, elem_classes="app-sidebar"):
            with gr.Column(elem_classes="sidebar-scroll"):
                gr.HTML('<div class="sidebar-section"><div class="sidebar-section-title">🧭 导航</div></div>')

                nav_radio = gr.Radio(
                    choices=[
                        ("⚔️ 对战", "arena"),
                        ("💬 单聊", "single"),
                        ("🏆 排行", "leaderboard"),
                        ("📊 基准", "benchmark"),
                        ("📦 模型", "models"),
                    ],
                    value="arena",
                    label="",
                    elem_id="nav-radio"
                )

                gr.HTML('<div class="sidebar-section"><div class="sidebar-section-title">🤖 模型选择</div></div>')

                model_selector = gr.CheckboxGroup(
                    label="🎯 对战模型",
                    choices=[(spec.label, spec.path) for spec in initial_specs],
                    value=[spec.path for spec in initial_specs],
                    elem_id="arena-model-selector",
                )

                single_model_selector = gr.Dropdown(
                    label="🎯 单聊模型",
                    choices=[(spec.label, spec.path) for spec in initial_specs],
                    value=initial_specs[0].path if initial_specs else None,
                    visible=False,
                    elem_id="single-model-selector",
                )

                with gr.Row(elem_classes="sidebar-btn-row"):
                    refresh_btn = gr.Button("🔄 刷新", variant="secondary", size="sm")
                    select_all_btn = gr.Button("☑️ 全选", variant="secondary", size="sm")
                    deselect_all_btn = gr.Button("⬜ 清空", variant="secondary", size="sm")

                model_scan_status = gr.Markdown(f"🔍 已发现 **{len(initial_specs)}** 个模型", elem_classes="status-text")

                gr.HTML('<div class="sidebar-section"><div class="sidebar-section-title">📝 系统提示词</div></div>')

                system_prompt = gr.Textbox(
                    label="",
                    value=DEFAULT_SYSTEM_PROMPT,
                    lines=2,
                    elem_id="system-box"
                )

                gr.HTML(render_prompt_templates())

                gr.HTML('<div class="sidebar-section"><div class="sidebar-section-title">⚙️ 推理参数</div></div>')

                with gr.Accordion("🔧 高级参数", open=False):
                    n_ctx = gr.Slider(2048, 32768, value=8192, step=512, label="📏 n_ctx 上下文长度")
                    max_tokens = gr.Slider(128, 8192, value=2048, step=128, label="📝 max_tokens 最大生成")
                    n_batch = gr.Slider(64, 2048, value=512, step=64, label="📦 n_batch 批次大小")
                    n_gpu_layers = gr.Slider(-1, 256, value=-1, step=1, label="🎮 n_gpu_layers GPU层数")
                    temperature = gr.Slider(0.0, 1.5, value=0.7, step=0.05, label="🌡️ temperature 温度")
                    top_p = gr.Slider(0.1, 1.0, value=0.95, step=0.05, label="🎯 top_p 核采样")
                    repeat_penalty = gr.Slider(1.0, 1.5, value=1.05, step=0.01, label="🔁 repeat_penalty 重复惩罚")
                    seed = gr.Number(value=-1, precision=0, label="🎲 seed (-1随机)")

        with gr.Column(scale=1, elem_classes="app-main"):
            with gr.Column(visible=True, elem_classes="view-panel") as view_arena:
                with gr.Column(elem_classes="main-content"):
                    stats_display = gr.HTML("")
                    chat_display = gr.HTML(render_multi_chat({}, {}))
                    with gr.Row():
                        export_display = gr.HTML("")

                with gr.Column(elem_classes="main-input-area"):
                    with gr.Row(elem_classes="input-row"):
                        user_prompt = gr.Textbox(
                            show_label=False,
                            placeholder="💬 输入指令，按 Enter 发送...",
                            lines=3,
                            elem_id="chat-input",
                            scale=8,
                        )
                        with gr.Column(scale=1, min_width=80, elem_classes="input-btn-col"):
                            send_btn = gr.Button("⚡ 发送", variant="primary", size="sm")
                            clear_chat_btn = gr.Button("🗑️ 清空", variant="secondary", size="sm")
                    status_md = gr.Markdown("", elem_classes="status-text")

            with gr.Column(visible=False, elem_classes="view-panel") as view_single:
                with gr.Column(elem_classes="main-content"):
                    single_chat_display = gr.HTML(render_single_chat([], "未选择", ""))

                with gr.Column(elem_classes="main-input-area"):
                    with gr.Row(elem_classes="input-row"):
                        single_input = gr.Textbox(
                            show_label=False,
                            placeholder="💬 输入消息，按 Enter 发送...",
                            lines=2,
                            elem_id="chat-input-single",
                            scale=8,
                        )
                        with gr.Column(scale=1, min_width=80, elem_classes="input-btn-col"):
                            single_send_btn = gr.Button("⚡ 发送", variant="primary", size="sm")
                            single_clear_btn = gr.Button("🗑️ 清空", variant="secondary", size="sm")
                    single_status = gr.Markdown("", elem_classes="status-text")

            with gr.Column(visible=False, elem_classes="view-panel") as view_leaderboard:
                with gr.Column(elem_classes="main-content"):
                    leaderboard_html = gr.HTML(render_leaderboard())
                with gr.Row(elem_classes="main-input-area"):
                    refresh_lb_btn = gr.Button("🔄 刷新排行榜", variant="secondary", size="sm")
                    clear_lb_btn = gr.Button("🗑️ 清空所有记录", variant="secondary", size="sm")

            with gr.Column(visible=False, elem_classes="view-panel") as view_benchmark:
                with gr.Column(elem_classes="main-content"):
                    gr.HTML(
                        '<div class="bench-info">'
                        '🧪 基准测试将独占执行，依次对选中的模型进行极限上下文、吞吐量、大海捞针及各项边界能力测试。<br>'
                        '⚠️ <strong>测试期间请勿进行其他操作</strong>，每个模型预计需要 1-3 分钟~'
                        '</div>'
                    )
                    bench_status = gr.Markdown("")
                    benchmark_table = gr.HTML(render_benchmark_table())
                with gr.Row(elem_classes="main-input-area"):
                    run_bench_btn = gr.Button("▶️ 开始基准测试", variant="primary", size="sm")
                    refresh_bench_btn = gr.Button("🔄 刷新", variant="secondary", size="sm")

            with gr.Column(visible=False, elem_classes="view-panel") as view_models:
                with gr.Column(elem_classes="main-content"):
                    model_cards_display = gr.HTML(render_model_cards(initial_specs))

    gr.HTML(render_sidebar_nav_js())
    gr.HTML(render_auto_scroll_js())

    nav_radio.change(
        fn=change_view,
        inputs=[nav_radio],
        outputs=[view_arena, view_single, view_leaderboard, view_benchmark, view_models, model_selector, single_model_selector]
    )

    send_btn.click(
        fn=multi_chat_sequential,
        inputs=[
            model_selector, user_prompt, system_prompt, n_ctx, max_tokens,
            temperature, top_p, repeat_penalty, n_gpu_layers, n_batch, seed, chat_histories
        ],
        outputs=[user_prompt, chat_histories, chat_display, stats_display, export_display, status_md],
    )

    user_prompt.submit(
        fn=multi_chat_sequential,
        inputs=[
            model_selector, user_prompt, system_prompt, n_ctx, max_tokens,
            temperature, top_p, repeat_penalty, n_gpu_layers, n_batch, seed, chat_histories
        ],
        outputs=[user_prompt, chat_histories, chat_display, stats_display, export_display, status_md],
    )

    clear_chat_btn.click(
        fn=clear_multi_chat,
        inputs=None,
        outputs=[chat_histories, chat_display, stats_display, export_display, status_md],
    )

    single_send_btn.click(
        fn=single_chat_stream,
        inputs=[
            single_model_selector, single_input, system_prompt, n_ctx, max_tokens,
            temperature, top_p, repeat_penalty, n_gpu_layers, n_batch, seed, single_messages
        ],
        outputs=[single_messages, single_chat_display, single_status],
    )

    single_input.submit(
        fn=single_chat_stream,
        inputs=[
            single_model_selector, single_input, system_prompt, n_ctx, max_tokens,
            temperature, top_p, repeat_penalty, n_gpu_layers, n_batch, seed, single_messages
        ],
        outputs=[single_messages, single_chat_display, single_status],
    )

    single_clear_btn.click(
        fn=clear_single_chat,
        inputs=None,
        outputs=[single_messages, single_chat_display, single_status],
    )

    refresh_btn.click(
        fn=refresh_model_choices,
        inputs=None,
        outputs=[model_selector, single_model_selector, model_scan_status, model_cards_display],
    )

    def select_all_models():
        specs = discover_models()
        return gr.update(value=[s.path for s in specs])

    def deselect_all_models():
        return gr.update(value=[])

    select_all_btn.click(fn=select_all_models, inputs=None, outputs=[model_selector])
    deselect_all_btn.click(fn=deselect_all_models, inputs=None, outputs=[model_selector])

    refresh_lb_btn.click(
        fn=lambda: render_leaderboard(),
        inputs=None,
        outputs=[leaderboard_html],
    )

    def clear_leaderboard():
        from storage import save_results_db
        save_results_db([])
        return render_leaderboard()

    clear_lb_btn.click(
        fn=clear_leaderboard,
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
    print(f"🚀 正在启动 {APP_TITLE} ...")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7866,
        share=False,
        theme=gr.themes.Base(
            primary_hue="blue",
            secondary_hue="gray",
            neutral_hue="slate",
        ),
        css=CUSTOM_CSS,
    )
