from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from arena.models import ModelSpec, discover_models
from arena.storage import load_benchmark_db, load_results_db


def render_markdown_to_html(text: str) -> str:
    result = text

    code_blocks: list[str] = []
    def _save_code_block(m: re.Match) -> str:
        lang = m.group(1) or ""
        code = m.group(2)
        idx = len(code_blocks)
        code_blocks.append((lang, code))
        return f"%%CODEBLOCK_{idx}%%"
    result = re.sub(r"```(\w*)\s*\n(.*?)```", _save_code_block, result, flags=re.DOTALL)

    inline_code_blocks: list[str] = []
    def _save_inline(m: re.Match) -> str:
        idx = len(inline_code_blocks)
        inline_code_blocks.append(m.group(1))
        return f"%%INLINE_{idx}%%"
    result = re.sub(r"`([^`]+)`", _save_inline, result)

    result = html.escape(result)

    result = re.sub(r"^### (.+)$", r'<h3>\1</h3>', result, flags=re.MULTILINE)
    result = re.sub(r"^## (.+)$", r'<h2>\1</h2>', result, flags=re.MULTILINE)
    result = re.sub(r"^# (.+)$", r'<h1>\1</h1>', result, flags=re.MULTILINE)

    result = re.sub(r"\*\*\*(.+?)\*\*\*", r'<strong><em>\1</em></strong>', result)
    result = re.sub(r"\*\*(.+?)\*\*", r'<strong>\1</strong>', result)
    result = re.sub(r"\*(.+?)\*", r'<em>\1</em>', result)

    result = re.sub(r"^\- (.+)$", r'<li>\1</li>', result, flags=re.MULTILINE)
    result = re.sub(r"^\d+\. (.+)$", r'<li>\1</li>', result, flags=re.MULTILINE)

    result = re.sub(r"^&gt; (.+)$", r'<blockquote>\1</blockquote>', result, flags=re.MULTILINE)

    result = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2" target="_blank" style="color:var(--accent-hover);text-decoration:none;">\1</a>', result)

    lines = result.split("\n")
    processed: list[str] = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("<li>"):
            if not in_list:
                processed.append("<ul>")
                in_list = True
            processed.append(stripped)
        else:
            if in_list and not stripped.startswith("</li>"):
                processed.append("</ul>")
                in_list = False
            if stripped and not stripped.startswith("<"):
                processed.append(f"<p>{stripped}</p>")
            else:
                processed.append(line)
    if in_list:
        processed.append("</ul>")
    result = "\n".join(processed)

    for idx, (lang, code) in enumerate(code_blocks):
        escaped_code = html.escape(code).strip()
        lang_label = lang.upper() if lang else "CODE"
        code_html = f'''<div class="code-block-wrapper">
  <div class="code-block-header">
    <span>📝 {html.escape(lang_label)}</span>
    <button class="copy-code-btn" onclick="navigator.clipboard.writeText(this.closest('.code-block-wrapper').querySelector('code').textContent);this.textContent='✅ 已复制!';setTimeout(()=>this.textContent='📋 复制',1500)">📋 复制</button>
  </div>
  <pre><code class="language-{html.escape(lang)}">{escaped_code}</code></pre>
</div>'''
        result = result.replace(f"%%CODEBLOCK_{idx}%%", code_html)

    for idx, code in enumerate(inline_code_blocks):
        escaped_code = html.escape(code)
        result = result.replace(f"%%INLINE_{idx}%%", f"<code>{escaped_code}</code>")

    return result


def inject_html_preview(text: str) -> str:
    html_blocks = re.findall(r"```html\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)

    if not html_blocks and (text.strip().lower().startswith("<!doctype html>") or text.strip().lower().startswith("<html")):
        html_blocks = [text.strip()]

    if html_blocks:
        btns = []
        for i, block in enumerate(html_blocks):
            import base64
            encoded_html = base64.b64encode(block.encode('utf-8')).decode('utf-8')
            btns.append(f'''
            <button onclick="
                const win = window.open('', '_blank');
                win.document.write(decodeURIComponent(escape(atob('{encoded_html}'))));
                win.document.close();
            " class="html-preview-btn">🚀 预览 HTML ({i+1})</button>
            ''')

        return f'<div class="html-preview-container">{"".join(btns)}</div>'

    return ""


def render_bot_content(text: str) -> str:
    preview_html = inject_html_preview(text)
    rendered = render_markdown_to_html(text)
    return preview_html + rendered


def render_header_html() -> str:
    return """
    <div class="app-header">
        <div class="header-left">
            <div class="header-logo">🐾</div>
            <span class="header-title">Arena Pro</span>
            <span class="header-version">v3 ✨</span>
        </div>
        <div class="header-right">
            <div class="header-status-dot"></div>
            <span class="header-status-text">💚 系统就绪</span>
        </div>
    </div>
    """


def render_leaderboard() -> str:
    db = load_results_db()
    if not db:
        return '<div class="empty-state"><div class="empty-title">📭 暂无历史记录</div><div class="empty-subtitle">🌸 完成对战后，战绩将自动记录于此~</div></div>'

    rows = []
    for entry in reversed(db[-50:]):
        models = entry.get("models", [])
        winner = entry.get("winner", "-")
        prompt = html.escape(entry.get("prompt", "")[:60]) + ("..." if len(entry.get("prompt", "")) > 60 else "")
        results = entry.get("results", [])
        total = len(results)
        success = len([r for r in results if r.get("status") == "已完成"])
        best_tps = max([r.get("tps", 0) for r in results] or [0])

        winner_badge = ""
        if winner and winner != "-":
            winner_badge = f'<span class="winner-badge">🏆 {html.escape(winner)}</span>'

        success_rate = f"{success}/{total}" if total > 0 else "0/0"
        success_color = "var(--green)" if success == total and total > 0 else "var(--text-secondary)"

        rows.append(
            f"""
            <tr>
              <td><span style="font-family:var(--font-mono);font-size:9px;color:var(--text-muted)">{html.escape(entry.get('time',''))}</span></td>
              <td><span style="font-size:10px">{html.escape(', '.join(models))}</span></td>
              <td>{winner_badge or f'<span style="color:var(--text-muted)">{html.escape(winner)}</span>'}</td>
              <td><span style="font-size:10px">{prompt}</span></td>
              <td><span style="color:{success_color};font-weight:600">{success_rate}</span></td>
              <td><span style="font-family:var(--font-mono);color:var(--accent-hover);font-weight:600">{best_tps:.1f}</span> <span style="color:var(--text-muted);font-size:8px">t/s</span></td>
            </tr>
            """
        )

    return f"""
    <div style="overflow-x:auto;max-height:calc(100vh - 200px);overflow-y:auto">
    <table class="leaderboard-table">
      <thead>
        <tr>
          <th>🕐 时间</th>
          <th>🤖 参战模型</th>
          <th>👑 优胜</th>
          <th>💬 Prompt</th>
          <th>✅ 成功率</th>
          <th>⚡ 峰值速度</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    </div>
    """


def render_benchmark_table() -> str:
    db = load_benchmark_db()
    if not db:
        return '<div class="empty-state"><div class="empty-title">🧪 暂无基准测试数据</div><div class="empty-subtitle">🎯 点击"运行边界能力检测"开始测试~</div></div>'

    rows = []
    for name, data in db.items():
        needle = '<span style="color:var(--green)">✅</span>' if data.get('needle_pass') else '<span style="color:var(--red)">❌</span>'
        json_ok = '<span style="color:var(--green)">✅</span>' if data.get('json_adherence') else '<span style="color:var(--red)">❌</span>'
        math_ok = '<span style="color:var(--green)">✅</span>' if data.get('math_logic') else '<span style="color:var(--red)">❌</span>'
        multi_ok = '<span style="color:var(--green)">✅</span>' if data.get('multilingual') else '<span style="color:var(--red)">❌</span>'

        logprob = data.get('logprob', 0)
        logprob_color = "var(--green)" if logprob > -1.0 else "var(--amber)" if logprob > -2.0 else "var(--red)"

        rows.append(
            f"""
            <tr>
              <td><strong style="color:var(--text-primary)">{html.escape(name)}</strong></td>
              <td><span style="font-family:var(--font-mono)">{data.get('vram_mb',0):.0f}</span></td>
              <td><span style="font-family:var(--font-mono)">{data.get('max_context',0):,}</span></td>
              <td><span style="font-family:var(--font-mono);color:var(--accent-hover)">{data.get('prefill_2k',0):.0f}</span></td>
              <td><span style="font-family:var(--font-mono);color:var(--green)">{data.get('decode_512',0):.1f}</span></td>
              <td><span style="font-family:var(--font-mono)">{data.get('ttft_ms',0):.0f}</span></td>
              <td>{needle}</td>
              <td><span style="font-family:var(--font-mono);color:{logprob_color}">{logprob:.3f}</span></td>
              <td>{json_ok}</td>
              <td>{math_ok}</td>
              <td>{multi_ok}</td>
            </tr>
            """
        )

    return f"""
    <div style="overflow-x:auto;max-height:calc(100vh - 200px);overflow-y:auto">
    <table class="leaderboard-table">
      <thead>
        <tr>
          <th>🏷️ 模型</th>
          <th>💾 VRAM</th>
          <th>📏 MaxCtx</th>
          <th>⚡ Prefill2K</th>
          <th>🔄 Decode512</th>
          <th>⏱️ TTFT</th>
          <th>🔍 Needle</th>
          <th>📊 Logprob</th>
          <th>📋 JSON</th>
          <th>🧮 逻辑</th>
          <th>🌍 多语言</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    </div>
    """


def render_stats_dashboard(histories: dict[str, list[dict[str, str]]], statuses: dict[str, dict[str, str]]) -> str:
    if not histories:
        return ""

    active_models = [m for m in histories.keys() if m in statuses]
    total_models = len(active_models)
    done = sum(1 for m in active_models if statuses.get(m, {}).get("status") == "已完成")
    generating = sum(1 for m in active_models if statuses.get(m, {}).get("status") == "生成中")
    failed = sum(1 for m in active_models if statuses.get(m, {}).get("status") == "失败")

    best_tps = 0.0
    for m in active_models:
        tps = statuses.get(m, {}).get("tps", 0)
        if isinstance(tps, (int, float)) and tps > best_tps:
            best_tps = tps

    total_tokens = sum(len(histories[m]) for m in active_models)

    generating_pct = (generating / max(total_models, 1)) * 100

    return f"""
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">🤖 模型</div>
        <div class="stat-value">{total_models}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">✅ 完成</div>
        <div class="stat-value ok">{done}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">🔄 生成中</div>
        <div class="stat-value accent">{generating}</div>
        <div class="progress-bar"><div class="progress-bar-fill" style="width:{generating_pct}%"></div></div>
      </div>
      <div class="stat-card">
        <div class="stat-label">❌ 失败</div>
        <div class="stat-value warn">{failed}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">⚡ 峰值</div>
        <div class="stat-value accent">{best_tps:.1f}</div>
        <div class="stat-delta">t/s</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">💬 消息</div>
        <div class="stat-value">{total_tokens}</div>
      </div>
    </div>
    """


def render_comparison(histories: dict[str, list[dict[str, str]]], statuses: dict[str, dict[str, str]]) -> str:
    if not histories or not statuses:
        return ""

    active_models = [m for m in histories.keys() if m in statuses and statuses[m].get("status") == "已完成"]
    if len(active_models) < 2:
        return ""

    metrics = []
    for m in active_models:
        s = statuses.get(m, {})
        msg_count = len([msg for msg in histories.get(m, []) if msg.get("role") == "assistant"])
        last_answer = ""
        for msg in reversed(histories.get(m, [])):
            if msg.get("role") == "assistant":
                last_answer = msg.get("content", "")
                break

        metrics.append({
            "name": m,
            "tps": s.get("tps", 0),
            "elapsed": s.get("elapsed", "-"),
            "msg_count": msg_count,
            "answer_length": len(last_answer),
        })

    best_tps = max(metrics, key=lambda x: x["tps"])
    fastest = min(metrics, key=lambda x: float(x["elapsed"].replace("s", "")) if x["elapsed"] != "-" else 9999)
    longest = max(metrics, key=lambda x: x["answer_length"])

    rows = []
    for m in metrics:
        badges = []
        if m["name"] == best_tps["name"]:
            badges.append('<span style="color:var(--accent-hover)">🏆 最快生成</span>')
        if m["name"] == fastest["name"]:
            badges.append('<span style="color:var(--green)">⚡ 最短耗时</span>')
        if m["name"] == longest["name"]:
            badges.append('<span style="color:var(--amber)">📝 最长回答</span>')

        badge_html = " · ".join(badges) if badges else ""

        rows.append(f"""
        <div class="compare-metric">
          <div>
            <span style="font-weight:700;color:var(--text-primary);font-size:10px">{html.escape(m['name'])}</span>
            {f'<div style="font-size:8px;margin-top:1px">{badge_html}</div>' if badge_html else ''}
          </div>
          <div style="display:flex;gap:10px;align-items:center">
            <span class="compare-metric-value" style="color:var(--accent-hover)">{m['tps']:.1f} t/s</span>
            <span class="compare-metric-value" style="color:var(--green)">{m['elapsed']}</span>
            <span class="compare-metric-value" style="color:var(--text-tertiary)">{m['answer_length']} 字</span>
          </div>
        </div>
        """)

    return f"""
    <div class="compare-panel" style="margin-top:10px">
      <div class="compare-header">
        <div class="panel-title-icon"></div>
        <div class="compare-title">📊 模型对比分析</div>
      </div>
      {''.join(rows)}
    </div>
    """


def _render_chat_messages(messages: list[dict[str, str]], model_name: str) -> str:
    chat_lines = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "system":
            continue

        is_user = role == "user"
        prefix = "🧑 You" if is_user else f"🤖 {html.escape(model_name)}"
        msg_class = "msg-user" if is_user else "msg-bot"

        if is_user:
            display_content = html.escape(content).replace("\n", "<br>")
        else:
            display_content = render_bot_content(content)

        chat_lines.append(f"""
        <div class="chat-msg {msg_class}">
            <div class="msg-author">{prefix}</div>
            <div class="msg-content">{display_content}</div>
        </div>
        """)
    return "".join(chat_lines)


def render_multi_chat(histories: dict[str, list[dict[str, str]]], statuses: dict[str, dict[str, str]]) -> str:
    active_models = [m for m in histories.keys() if (not statuses or m in statuses)]
    if not histories or not active_models:
        return """
        <div class="empty-state">
          <div class="empty-title">💭 等待指令输入</div>
          <div class="empty-subtitle">✨ 输入内容后，系统将按顺序调度所选模型进行独立上下文对话~</div>
        </div>
        """

    cards: list[str] = []
    for model_name in active_models:
        messages = histories[model_name]
        info = statuses.get(model_name, {})
        status_text = info.get("status", "等待中")
        perf_text = info.get("perf", "")

        status_class = {
            "等待中": "status-waiting",
            "加载中": "status-loading",
            "生成中": "status-generating",
            "已完成": "status-done",
            "失败": "status-failed",
        }.get(status_text, "status-waiting")

        status_emoji = {
            "等待中": "⏳",
            "加载中": "📦",
            "生成中": "✍️",
            "已完成": "✅",
            "失败": "❌",
        }.get(status_text, "⏳")

        badges = f'<span class="status-pill {status_class}">{status_emoji} {html.escape(status_text)}</span>'
        if perf_text:
            badges += f'<span class="meta-badge size" style="margin-bottom:0">{html.escape(perf_text)}</span>'

        chat_html = _render_chat_messages(messages, model_name)

        typing_html = ""
        if status_text == "生成中":
            typing_html = """
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <span>✍️ 生成中...</span>
            </div>
            """

        cards.append(f"""
        <div class="result-card chat-col-card" style="padding:0;overflow:hidden;display:flex;flex-direction:column">
            <div class="chat-header">
                <div class="chat-model-name">🤖 {html.escape(model_name)}</div>
                <div class="chat-model-status">{badges}</div>
            </div>
            <div class="chat-history">
                {chat_html}
                {typing_html}
            </div>
        </div>
        """)

    return f'<div class="result-grid">{"".join(cards)}</div>'


def render_single_chat(messages: list[dict[str, str]], model_name: str, status: str = "", perf: str = "") -> str:
    if not messages:
        return """
        <div class="empty-state">
          <div class="empty-title">💬 开始对话</div>
          <div class="empty-subtitle">🌸 输入消息与模型进行一对一聊天~</div>
        </div>
        """

    status_class = {
        "等待中": "status-waiting",
        "加载中": "status-loading",
        "生成中": "status-generating",
        "已完成": "status-done",
        "失败": "status-failed",
    }.get(status, "status-waiting")

    status_emoji = {
        "等待中": "⏳",
        "加载中": "📦",
        "生成中": "✍️",
        "已完成": "✅",
        "失败": "❌",
    }.get(status, "⏳")

    badges = f'<span class="status-pill {status_class}">{status_emoji} {html.escape(status)}</span>' if status else ""
    if perf:
        badges += f'<span class="meta-badge size" style="margin-bottom:0">{html.escape(perf)}</span>'

    chat_html = _render_chat_messages(messages, model_name)

    typing_html = ""
    if status == "生成中":
        typing_html = """
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <span>✍️ 生成中...</span>
        </div>
        """

    return f"""
    <div class="single-chat-wrapper">
      <div class="chat-col-card" style="height:100%;max-height:none">
        <div class="chat-header">
            <div class="chat-model-name">🤖 {html.escape(model_name)}</div>
            <div class="chat-model-status">{badges}</div>
        </div>
        <div class="chat-history">
            {chat_html}
            {typing_html}
        </div>
      </div>
    </div>
    """


def render_prompt_templates() -> str:
    templates = [
        {"name": "🌟 通用助手", "desc": "标准对话", "prompt": "你是一名专业、准确、简洁的中文助手。请优先直接回答用户问题；如果存在不确定性，请明确说明。"},
        {"name": "💻 代码专家", "desc": "编程解答", "prompt": "你是一名资深软件工程师，精通多种编程语言和技术栈。请提供清晰、可运行的代码示例，并解释关键逻辑。"},
        {"name": "🎨 创意写作", "desc": "文案创作", "prompt": "你是一名创意写作助手，擅长故事构思、文案创作和文学分析。请用生动有趣的语言回应，必要时提供多个创意方案。"},
        {"name": "🔬 学术分析", "desc": "深度分析", "prompt": "你是一名学术研究助手，擅长逻辑分析和深度思考。请提供结构化、有深度的回答，引用相关概念时简要解释。"},
        {"name": "🎭 角色扮演", "desc": "角色对话", "prompt": "你是一位经验丰富的导师，善于用启发式提问引导对方思考。不要直接给答案，而是通过提问帮助对方自己找到解决方案。"},
        {"name": "✂️ 简洁模式", "desc": "极简回答", "prompt": "你是一名极简主义助手。请用最简洁的语言回答，避免冗余。能用一句话就不用两句。"},
    ]

    cards = []
    for t in templates:
        escaped_prompt = html.escape(t["prompt"]).replace("'", "\\'").replace('"', '&quot;')
        cards.append(f"""
        <div class="template-card" onclick="var ta=document.querySelector('#system-box textarea');if(ta){{ta.value='{escaped_prompt}';ta.dispatchEvent(new Event('input',{{bubbles:true}}));}}">
            <div class="template-name">{html.escape(t['name'])}</div>
            <div class="template-desc">{html.escape(t['desc'])}</div>
        </div>
        """)

    return f'<div class="template-grid">{"".join(cards)}</div>'


def render_export_button(histories: dict[str, list[dict[str, str]]], mode: str = "multi") -> str:
    if not histories:
        return ""

    export_data = json.dumps(histories, ensure_ascii=False, indent=2)
    import base64
    encoded = base64.b64encode(export_data.encode('utf-8')).decode('utf-8')

    return f"""
    <a download="arena_chat_export.json" href="data:application/json;base64,{encoded}" class="export-btn" style="text-decoration:none">
        📥 导出对话
    </a>
    """


def render_model_cards(specs: list[ModelSpec]) -> str:
    if not specs:
        return '<div class="empty-state"><div class="empty-title">🔍 未发现模型</div><div class="empty-subtitle">📁 请检查模型目录是否正确配置~</div></div>'

    cards = []
    for i, spec in enumerate(specs):
        badges = []
        if spec.params:
            badges.append(f'<span class="meta-badge params">🔢 {html.escape(spec.params)}</span>')
        if spec.quant:
            badges.append(f'<span class="meta-badge quant">⚡ {html.escape(spec.quant)}</span>')
        if spec.size_gb > 0:
            badges.append(f'<span class="meta-badge size">💾 {spec.size_gb:.1f} GB</span>')

        cards.append(f"""
        <div class="model-card">
            <div class="model-index">#{i+1:02d}</div>
            <div class="model-name">🤖 {html.escape(spec.label.split('|')[0].strip())}</div>
            <div style="margin-bottom:3px">{"".join(badges)}</div>
            <div class="model-path">📂 {html.escape(spec.relative_path)}</div>
        </div>
        """)

    return f'<div class="model-grid">{"".join(cards)}</div>'


def render_sidebar_nav_js() -> str:
    return """
    <script>
    (function() {
        function initNav() {
            const container = document.querySelector('#nav-radio');
            if (!container) return;
            const labels = container.querySelectorAll('label');
            labels.forEach(l => {
                l.classList.add('nav-item');
                const icon = l.querySelector('span:first-child');
                if (icon) icon.classList.add('nav-icon');
            });
            const checked = container.querySelector('input[type="radio"]:checked');
            if (checked) {
                const checkedLabel = checked.closest('label');
                if (checkedLabel) checkedLabel.classList.add('selected');
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initNav);
        } else {
            initNav();
        }
        const observer = new MutationObserver(initNav);
        observer.observe(document.body, { childList: true, subtree: true });
    })();
    </script>
    """


def render_auto_scroll_js() -> str:
    return """
    <script>
    (function() {
        function autoScroll() {
            document.querySelectorAll('.chat-history').forEach(el => {
                el.scrollTop = el.scrollHeight;
            });
        }
        const observer = new MutationObserver(() => {
            requestAnimationFrame(autoScroll);
        });
        observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    })();
    </script>
    """
