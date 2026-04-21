from __future__ import annotations

import html
import re
import urllib.parse
from pathlib import Path
from typing import Any

from arena.models import ModelSpec, discover_models
from arena.storage import load_benchmark_db, load_results_db


def inject_html_preview(text: str) -> str:
    escaped_text = html.escape(text).replace("\n", "<br>")
    
    # 查找所有的 ```html ... ``` 块
    html_blocks = re.findall(r"```html\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    
    # 如果没有找到 ```html，但整个文本像是 HTML 文档
    if not html_blocks and (text.strip().lower().startswith("<!doctype html>") or text.strip().lower().startswith("<html")):
        html_blocks = [text.strip()]
        
    if html_blocks:
        btns = []
        for i, block in enumerate(html_blocks):
            # 将 HTML 内容 Base64 编码以防止被转义和截断
            import base64
            encoded_html = base64.b64encode(block.encode('utf-8')).decode('utf-8')
            # 直接通过 onclick 事件触发新窗口打开 Base64 内容
            btns.append(f'''
            <button onclick="
                const win = window.open('', '_blank');
                win.document.write(decodeURIComponent(escape(atob('{encoded_html}'))));
                win.document.close();
            " class="html-preview-btn">🚀 在新标签页中全屏预览 HTML ({i+1})</button>
            ''')
        
        # 将按钮注入到回答的最上方
        escaped_text = f'<div class="html-preview-container">{"".join(btns)}</div>' + escaped_text
        
    return escaped_text

def render_leaderboard() -> str:
    db = load_results_db()
    if not db:
        return '<div class="empty-state"><div class="empty-title">暂无历史记录</div></div>'
    rows = []
    for entry in db[-20:]:
        models = entry.get("models", [])
        winner = entry.get("winner", "-")
        prompt = html.escape(entry.get("prompt", "")[:40]) + "..."
        rows.append(
            f"""
            <tr>
              <td>{html.escape(entry.get('time',''))}</td>
              <td>{html.escape(', '.join(models))}</td>
              <td>{html.escape(winner)}</td>
              <td>{prompt}</td>
            </tr>
            """
        )
    return f"""
    <table class="leaderboard-table">
      <thead>
        <tr><th>时间</th><th>参战模型</th><th>优胜</th><th>Prompt</th></tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    """


def render_benchmark_table() -> str:
    db = load_benchmark_db()
    if not db:
        return '<div class="empty-state"><div class="empty-title">暂无基准测试数据</div><div class="empty-subtitle">点击"运行边界能力检测"开始测试。</div></div>'
    rows = []
    for name, data in db.items():
        rows.append(
            f"""
            <tr>
              <td>{html.escape(name)}</td>
              <td>{data.get('vram_mb',0):.0f}</td>
              <td>{data.get('max_context',0):,}</td>
              <td>{data.get('prefill_2k',0):.0f}</td>
              <td>{data.get('decode_512',0):.1f}</td>
              <td>{data.get('ttft_ms',0):.0f}</td>
              <td>{'✅' if data.get('needle_pass') else '❌'}</td>
              <td>{data.get('logprob',0):.3f}</td>
              <td>{'✅' if data.get('json_adherence') else '❌'}</td>
              <td>{'✅' if data.get('math_logic') else '❌'}</td>
              <td>{'✅' if data.get('multilingual') else '❌'}</td>
            </tr>
            """
        )
    return f"""
    <table class="leaderboard-table">
      <thead>
        <tr>
          <th>模型</th><th>VRAM(MiB)</th><th>MaxCtx</th>
          <th>Prefill2K</th><th>Decode512</th><th>TTFT(ms)</th>
          <th>Needle</th><th>Logprob</th>
          <th>JSON</th><th>逻辑</th><th>多语言</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    """


def render_multi_chat(histories: dict[str, list[dict[str, str]]], statuses: dict[str, dict[str, str]]) -> str:
    active_models = [m for m in histories.keys() if (not statuses or m in statuses)]
    if not histories or not active_models:
        return """
        <div class="empty-state">
          <div class="empty-title">等待指令输入</div>
          <div class="empty-subtitle">输入内容后，系统将按顺序调度所选模型进行独立上下文对话。</div>
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
        
        badges = f'<span class="status-pill {status_class}">{html.escape(status_text)}</span>'
        if perf_text:
            badges += f'<span class="meta-badge size" style="margin-bottom:0;">{html.escape(perf_text)}</span>'
            
        chat_lines = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "system":
                continue  # 隐藏 system prompt，不显示在聊天流中
            
            is_user = role == "user"
            prefix = "👤 User" if is_user else f"🤖 {html.escape(model_name)}"
            msg_class = "msg-user" if is_user else "msg-bot"
            
            # 只有 assistant 的消息需要渲染 HTML 预览
            display_content = html.escape(content).replace("\n", "<br>") if is_user else inject_html_preview(content)
            
            chat_lines.append(f"""
            <div class="chat-msg {msg_class}">
                <div class="msg-author">{prefix}</div>
                <div class="msg-content">{display_content}</div>
            </div>
            """)
            
        cards.append(f"""
        <div class="result-card chat-col-card" style="padding: 0; overflow: hidden; display: flex; flex-direction: column;">
            <div class="chat-header">
                <div class="chat-model-name">{html.escape(model_name)}</div>
                <div class="chat-model-status">{badges}</div>
            </div>
            <div class="chat-history" style="flex: 1; border-radius: 0; border: none; background: transparent;">
                {"".join(chat_lines)}
            </div>
        </div>
        """)
        
    return f'<div class="result-grid">{"".join(cards)}</div>'
