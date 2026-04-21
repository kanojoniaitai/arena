from __future__ import annotations

import html
import re
import urllib.parse
from pathlib import Path
from typing import Any

from arena.models import ModelSpec, discover_models
from arena.storage import load_benchmark_db, load_results_db


def render_model_gallery(specs: list[ModelSpec]) -> str:
    if not specs:
        return """
        <div class="empty-state">
          <div class="empty-title">没有找到可用的 GGUF 聊天模型</div>
          <div class="empty-subtitle">请确认模型位于 E:\\local_LLM\\Models_Repo，且文件名不是 mmproj。</div>
        </div>
        """
    cards: list[str] = []
    for index, spec in enumerate(specs, start=1):
        meta_badges = ""
        if spec.params:
            meta_badges += f'<span class="meta-badge params">{html.escape(spec.params)}</span>'
        if spec.quant:
            meta_badges += f'<span class="meta-badge quant">{html.escape(spec.quant)}</span>'
        meta_badges += f'<span class="meta-badge size">{spec.size_gb:.1f} GB</span>'
        cards.append(
            f"""
            <div class="model-card">
              <div class="model-index">#{index:02d}</div>
              <div class="model-name">{html.escape(Path(spec.path).stem)}</div>
              <div class="model-meta">{meta_badges}</div>
              <div class="model-path">{html.escape(spec.relative_path)}</div>
            </div>
            """
        )
    return f'<div class="model-grid">{"".join(cards)}</div>'


def inject_html_preview(text: str) -> str:
    escaped_text = html.escape(text).replace("\n", "<br>")
    
    html_blocks = re.findall(r"```html\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if not html_blocks and (text.strip().lower().startswith("<!doctype html>") or text.strip().lower().startswith("<html")):
        html_blocks = [text.strip()]
        
    if html_blocks:
        btns = []
        for i, block in enumerate(html_blocks):
            encoded_html = urllib.parse.quote(block)
            data_uri = f"data:text/html;charset=utf-8,{encoded_html}"
            btns.append(f'<a href="{data_uri}" target="_blank" class="html-preview-btn">🚀 新标签页打开 HTML 预览</a>')
        
        escaped_text = f'<div class="html-preview-container">{"".join(btns)}</div>' + escaped_text
        
    return escaped_text

def render_result_cards(results: list[dict[str, Any]]) -> str:
    if not results:
        return """
        <div class="empty-state">
          <div class="empty-title">等待开始对比</div>
          <div class="empty-subtitle">输入指令后，程序会按顺序加载每个模型，并在独立上下文中分别生成答案。</div>
        </div>
        """
    cards: list[str] = []
    for item in results:
        status_class = {
            "等待中": "status-waiting",
            "加载中": "status-loading",
            "生成中": "status-generating",
            "已完成": "status-done",
            "失败": "status-failed",
        }.get(item["status"], "status-waiting")
        elapsed = item.get("elapsed", "")
        elapsed_badge = f'<span class="mini-badge">{html.escape(elapsed)}</span>' if elapsed else ""
        perf = item.get("perf", "")
        perf_badge = f'<span class="mini-badge perf">{html.escape(perf)}</span>' if perf else ""
        answer = inject_html_preview(item.get("answer", ""))
        detail = html.escape(item.get("detail", ""))
        cards.append(
            f"""
            <div class="result-card">
              <div class="result-card-header">
                <div>
                  <div class="result-title">{html.escape(item["name"])}</div>
                  <div class="result-subtitle">{html.escape(item["path"])}</div>
                </div>
                <div class="result-badges">
                  <span class="status-pill {status_class}">{html.escape(item["status"])}</span>
                  {elapsed_badge}
                  {perf_badge}
                </div>
              </div>
              <div class="result-detail">{detail}</div>
              <div class="result-answer">{answer or "..."}</div>
            </div>
            """
        )
    return f'<div class="result-grid">{"".join(cards)}</div>'


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


def render_chat_history(messages_text: str, model_info: dict[str, Any]) -> str:
    loaded = model_info.get("loaded", False)
    name = model_info.get("name", "未选择")
    status_color = "#57d39b" if loaded else "#ff7b8c"
    status_text = "已加载" if loaded else "未加载"
    badges = f'<span style="color:{status_color};font-weight:700;">● {status_text}</span>'
    if model_info.get("params"):
        badges += f' <span class="meta-badge params">{html.escape(model_info["params"])}</span>'
    if model_info.get("quant"):
        badges += f' <span class="meta-badge quant">{html.escape(model_info["quant"])}</span>'
    history_html = inject_html_preview(messages_text)
    return f"""
    <div class="chat-header">
      <div class="chat-model-name">{html.escape(name)}</div>
      <div class="chat-model-status">{badges}</div>
    </div>
    <div class="chat-history">{history_html}</div>
    """
