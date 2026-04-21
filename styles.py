CUSTOM_CSS = """
/* RESET & FONTS */
:root {
  --bg-main: #09090b;
  --bg-panel: rgba(24, 24, 27, 0.65);
  --bg-card: rgba(39, 39, 42, 0.4);
  --bg-card-hover: rgba(39, 39, 42, 0.8);
  --line: rgba(255, 255, 255, 0.08);
  --line-strong: rgba(255, 255, 255, 0.15);
  --text-main: #fafafa;
  --text-soft: #a1a1aa;
  --accent: #3b82f6;
  --accent-hover: #60a5fa;
  --ok: #10b981;
  --warn: #f59e0b;
  --danger: #ef4444;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}

body {
  background-color: var(--bg-main) !important;
  color: var(--text-main) !important;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  background-image: 
    radial-gradient(circle at top center, rgba(59, 130, 246, 0.15) 0%, transparent 40%) !important;
}

/* GRADIO COMPONENT OVERRIDES (Vercel/Linear style) */
.gradio-container {
  max-width: 1280px !important;
  padding: 40px 24px !important;
}

/* Base Panel */
.panel {
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--bg-panel);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.panel-title::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 14px;
  background: var(--accent);
  border-radius: 2px;
}

/* Forms & Inputs */
#prompt-box textarea, 
#system-box textarea, 
#chat-input textarea,
.gr-box,
.gr-input,
.gr-text-input {
  background: rgba(0, 0, 0, 0.2) !important;
  border: 1px solid var(--line) !important;
  border-radius: var(--radius-md) !important;
  color: var(--text-main) !important;
  font-size: 14px !important;
  transition: all 0.2s ease !important;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1) !important;
}

#prompt-box textarea:focus, 
#system-box textarea:focus, 
#chat-input textarea:focus,
.gr-input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 1px var(--accent), inset 0 1px 2px rgba(0, 0, 0, 0.1) !important;
  outline: none !important;
}

/* Buttons */
.gr-button {
  border-radius: var(--radius-sm) !important;
  font-weight: 500 !important;
  font-size: 14px !important;
  transition: all 0.2s ease !important;
  border: 1px solid transparent !important;
}

.gr-button-primary {
  background: var(--text-main) !important;
  color: var(--bg-main) !important;
}
.gr-button-primary:hover {
  background: #e4e4e7 !important;
  transform: translateY(-1px);
}

.gr-button-secondary {
  background: transparent !important;
  border-color: var(--line) !important;
  color: var(--text-main) !important;
}
.gr-button-secondary:hover {
  background: rgba(255, 255, 255, 0.05) !important;
  border-color: var(--line-strong) !important;
}

/* Grids & Cards */
.model-grid, .result-grid {
  display: grid;
  gap: 16px;
}
.model-grid {
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}
.result-grid {
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
}

.model-card, .result-card {
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  padding: 20px;
  transition: all 0.2s ease;
}
.model-card:hover, .result-card:hover {
  background: var(--bg-card-hover);
  border-color: var(--line-strong);
}

.model-index {
  color: var(--text-soft);
  font-size: 12px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  margin-bottom: 8px;
}
.model-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 12px;
}
.model-path {
  color: var(--text-soft);
  font-size: 12px;
  font-family: ui-monospace, SFMono-Regular, monospace;
  word-break: break-all;
}

/* Badges */
.meta-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 500;
  font-family: ui-monospace, SFMono-Regular, monospace;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--line);
  margin-right: 6px;
  margin-bottom: 6px;
}
.meta-badge.params { color: #a1a1aa; }
.meta-badge.quant { color: #d4d4d8; }
.meta-badge.size { color: var(--ok); background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.2); }

/* Results specific */
.result-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 12px;
}
.result-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}
.result-subtitle {
  color: var(--text-soft);
  font-size: 12px;
  font-family: ui-monospace, SFMono-Regular, monospace;
}
.result-answer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--line);
  color: #e4e4e7;
  font-size: 14px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
}

.status-pill {
  padding: 4px 10px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 500;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
}
.status-done { color: var(--ok); background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.2); }
.status-generating { color: var(--accent); background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.2); animation: pulse 2s infinite; }
.status-failed { color: var(--danger); background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.2); }
.status-loading { color: var(--warn); background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.2); }
.status-waiting { color: var(--text-soft); background: rgba(255, 255, 255, 0.05); border-color: var(--line); }

/* Tables */
.leaderboard-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;
}
.leaderboard-table th {
  text-align: left;
  padding: 12px 16px;
  color: var(--text-soft);
  font-weight: 500;
  border-bottom: 1px solid var(--line);
}
.leaderboard-table td {
  padding: 16px;
  border-bottom: 1px solid var(--line);
  color: var(--text-main);
}
.leaderboard-table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

/* Chat */
.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chat-model-name {
  font-size: 16px;
  font-weight: 600;
}
.chat-history {
  padding: 20px;
  min-height: 400px;
  max-height: 600px;
  overflow-y: auto;
  line-height: 1.6;
  font-size: 14px;
  white-space: pre-wrap;
}

/* Empty States */
.empty-state {
  padding: 40px;
  text-align: center;
  border: 1px dashed var(--line-strong);
  border-radius: var(--radius-md);
  color: var(--text-soft);
}
.empty-title {
  color: var(--text-main);
  font-weight: 600;
  margin-bottom: 8px;
}
.empty-subtitle {
  font-size: 13px;
}

/* HTML Preview Feature */
.html-preview-container {
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.html-preview-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  background: var(--text-main);
  color: var(--bg-main) !important;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
}
.html-preview-btn:hover {
  background: #e4e4e7;
  transform: translateY(-1px);
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

/* Scrollbars */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
"""
