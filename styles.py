CUSTOM_CSS = """
:root {
  --bg-main: #07111f;
  --bg-panel: rgba(10, 20, 36, 0.88);
  --bg-card: linear-gradient(180deg, rgba(18, 32, 54, 0.98), rgba(10, 18, 32, 0.98));
  --line: rgba(115, 162, 255, 0.20);
  --line-strong: rgba(106, 182, 255, 0.38);
  --text-main: #eef4ff;
  --text-soft: #97a8c4;
  --accent: #7bc8ff;
  --accent-2: #9f7cff;
  --ok: #57d39b;
  --warn: #ffd166;
  --danger: #ff7b8c;
}
body {
  background:
    radial-gradient(circle at top left, rgba(123, 200, 255, 0.18), transparent 24%),
    radial-gradient(circle at top right, rgba(159, 124, 255, 0.18), transparent 20%),
    linear-gradient(180deg, #030814 0%, #07111f 100%) !important;
  color: var(--text-main) !important;
  font-family: "Segoe UI", "Microsoft YaHei", sans-serif !important;
}
.gradio-container {
  max-width: 1600px !important;
  padding: 18px !important;
}
.app-shell {
  border: 1px solid var(--line);
  background: rgba(5, 12, 24, 0.78);
  border-radius: 26px;
  padding: 14px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.34);
}
.hero {
  border: 1px solid var(--line);
  border-radius: 24px;
  padding: 24px 26px;
  background: linear-gradient(135deg, rgba(17, 30, 51, 0.92), rgba(10, 18, 32, 0.92));
  margin-bottom: 14px;
}
.hero-title {
  font-size: 34px;
  font-weight: 800;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
  background: linear-gradient(90deg, #ffffff, #7bc8ff, #b59cff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-subtitle {
  color: var(--text-soft);
  font-size: 14px;
  line-height: 1.8;
}
.panel {
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 16px;
  background: var(--bg-panel);
  backdrop-filter: blur(10px);
}
.panel-title {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: var(--accent);
  text-transform: uppercase;
  margin-bottom: 12px;
}
.stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin: 0 10px 10px 0;
  border-radius: 999px;
  border: 1px solid var(--line);
  color: var(--text-main);
  background: rgba(123, 200, 255, 0.08);
  font-size: 13px;
}
.model-grid, .result-grid {
  display: grid;
  gap: 14px;
}
.model-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}
.result-grid {
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
}
.model-card, .result-card {
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--bg-card);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
}
.model-card {
  padding: 16px;
}
.model-index {
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  margin-bottom: 12px;
}
.model-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 8px;
}
.model-meta {
  margin-bottom: 8px;
}
.meta-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  margin-right: 6px;
  font-weight: 600;
}
.meta-badge.params { background: rgba(123,200,255,0.15); color: #7bc8ff; }
.meta-badge.quant { background: rgba(159,124,255,0.15); color: #b59cff; }
.meta-badge.size { background: rgba(87,211,155,0.15); color: #57d39b; }
.model-path, .result-subtitle, .result-detail {
  color: var(--text-soft);
  font-size: 12px;
  line-height: 1.7;
}
.result-card {
  padding: 18px;
}
.result-card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}
.result-title {
  font-size: 16px;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 6px;
}
.result-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.status-pill, .mini-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid var(--line);
  white-space: nowrap;
}
.mini-badge.perf { background: rgba(87,211,155,0.12); color: #57d39b; }
.status-waiting { color: var(--text-soft); }
.status-loading { color: var(--warn); }
.status-generating { color: var(--accent); }
.status-done { color: var(--ok); }
.status-failed { color: var(--danger); }
.result-answer {
  margin-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 14px;
  color: #f6f8ff;
  line-height: 1.9;
  white-space: normal;
  word-break: break-word;
  max-height: 520px;
  overflow-y: auto;
}
.empty-state {
  padding: 32px;
  text-align: center;
  border: 1px dashed var(--line-strong);
  border-radius: 22px;
  color: var(--text-soft);
  background: rgba(9, 17, 31, 0.72);
}
.empty-title {
  color: var(--text-main);
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}
.empty-subtitle {
  font-size: 13px;
  line-height: 1.8;
}
.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  color: var(--text-main);
}
.leaderboard-table th {
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid var(--line);
  color: var(--accent);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 11px;
}
.leaderboard-table td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.chat-header {
  padding: 14px 18px;
  border-bottom: 1px solid var(--line);
  background: rgba(5,12,24,0.6);
  border-radius: 18px 18px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chat-model-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
}
.chat-model-status {
  font-size: 12px;
}
.chat-history {
  padding: 18px;
  min-height: 300px;
  max-height: 600px;
  overflow-y: auto;
  line-height: 1.9;
  white-space: pre-wrap;
  word-break: break-word;
}
#prompt-box textarea, #system-box textarea, #status-box textarea, #chat-input textarea {
  background: rgba(8, 18, 34, 0.92) !important;
  border: 1px solid var(--line) !important;
  color: var(--text-main) !important;
  border-radius: 18px !important;
}
#prompt-box textarea, #system-box textarea, #chat-input textarea {
  font-size: 15px !important;
  line-height: 1.8 !important;
}
.gr-button-primary {
  background: linear-gradient(90deg, #6bc7ff, #8b7dff) !important;
  color: #051120 !important;
  border: none !important;
  font-weight: 700 !important;
}
.gr-button-secondary {
  background: rgba(123, 200, 255, 0.08) !important;
  color: var(--text-main) !important;
  border: 1px solid var(--line) !important;
}
.gr-form, .gr-box, .gr-accordion {
  border-color: var(--line) !important;
}
"""
