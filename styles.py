CUSTOM_CSS = """
:root {
  /* Premium Dark Theme */
  --bg-main: #0a0a0c;
  --bg-panel: rgba(18, 18, 20, 0.6);
  --bg-card: linear-gradient(145deg, rgba(28, 28, 32, 0.9), rgba(20, 20, 22, 0.95));
  --line: rgba(255, 255, 255, 0.08);
  --line-strong: rgba(255, 255, 255, 0.15);
  --text-main: #f0f0f2;
  --text-soft: #a0a0a5;
  --accent: #5d5cff;
  --accent-hover: #7b7aff;
  --accent-2: #ff5c8d;
  --ok: #20e090;
  --warn: #ffb84d;
  --danger: #ff4d4d;
  --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  --btn-gradient: linear-gradient(135deg, #5d5cff 0%, #8b5cff 100%);
}

body {
  background-color: var(--bg-main) !important;
  background-image: 
    radial-gradient(circle at 15% 50%, rgba(93, 92, 255, 0.08), transparent 25%),
    radial-gradient(circle at 85% 30%, rgba(255, 92, 141, 0.06), transparent 25%) !important;
  background-attachment: fixed !important;
  color: var(--text-main) !important;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif !important;
  -webkit-font-smoothing: antialiased;
}

.gradio-container {
  max-width: 1440px !important;
  padding: 32px 24px !important;
}

/* Glassmorphism Shell */
.app-shell {
  border: 1px solid var(--line);
  background: var(--bg-panel);
  border-radius: 32px;
  padding: 24px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: var(--glass-shadow);
  transition: transform 0.3s ease;
}

/* Typography & Hero */
.hero {
  border: 1px solid var(--line);
  border-radius: 24px;
  padding: 40px 32px;
  background: linear-gradient(135deg, rgba(20, 20, 24, 0.8), rgba(10, 10, 12, 0.9));
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.hero-title {
  font-size: 42px;
  font-weight: 800;
  letter-spacing: -0.5px;
  margin-bottom: 12px;
  background: linear-gradient(to right, #ffffff 30%, #a0a0a5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  color: var(--text-soft);
  font-size: 16px;
  line-height: 1.6;
  max-width: 800px;
}

/* Panels */
.panel {
  border: 1px solid var(--line);
  border-radius: 24px;
  padding: 24px;
  background: var(--bg-panel);
  backdrop-filter: blur(12px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
}

.panel-title {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.15em;
  color: var(--accent);
  text-transform: uppercase;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Grids & Cards */
.model-grid, .result-grid {
  display: grid;
  gap: 20px;
}

.model-grid {
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}

.result-grid {
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
}

.model-card, .result-card {
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--bg-card);
  box-shadow: 0 4px 20px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.05);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.model-card:hover, .result-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
  border-color: var(--line-strong);
}

.model-card {
  padding: 20px;
}

.model-index {
  color: var(--text-soft);
  font-size: 12px;
  font-weight: 800;
  margin-bottom: 12px;
}

.model-name {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
  letter-spacing: -0.3px;
}

/* Badges */
.meta-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  margin-right: 8px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
}

.meta-badge.params { color: #a0a0a5; }
.meta-badge.quant { color: #d4d4d8; }
.meta-badge.size { color: var(--ok); border-color: rgba(32, 224, 144, 0.2); background: rgba(32, 224, 144, 0.05); }

/* Results */
.result-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.result-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 16px;
}

.result-title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
}

.result-subtitle {
  color: var(--text-soft);
  font-size: 13px;
  word-break: break-all;
}

.status-pill, .mini-badge {
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(0,0,0,0.3);
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}

.mini-badge.perf { background: rgba(32,224,144,0.1); color: var(--ok); border-color: rgba(32,224,144,0.2); }

.status-waiting { color: var(--text-soft); border-color: rgba(255,255,255,0.1); }
.status-loading { color: var(--warn); border-color: rgba(255,184,77,0.3); animation: pulse 1.5s infinite; }
.status-done { color: var(--ok); border-color: rgba(32,224,144,0.3); }
.status-generating { color: var(--accent); border-color: rgba(93,92,255,0.3); animation: pulse 2s infinite; }
.status-failed { color: var(--danger); border-color: rgba(255,77,77,0.3); }

.result-answer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--line);
  color: #e0e0e0;
  font-size: 15px;
  line-height: 1.8;
  max-height: 500px;
  overflow-y: auto;
  font-family: inherit;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: rgba(0,0,0,0.1);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.2);
}

/* HTML Preview Feature */
.html-preview-container {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.html-preview-btn {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: rgba(93, 92, 255, 0.1);
  border: 1px solid rgba(93, 92, 255, 0.4);
  border-radius: 12px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.html-preview-btn:hover {
  background: var(--accent);
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(93, 92, 255, 0.4);
}

/* Tables */
.leaderboard-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 14px;
}

.leaderboard-table th {
  text-align: left;
  padding: 16px;
  color: var(--text-soft);
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--line-strong);
}

.leaderboard-table td {
  padding: 16px;
  border-bottom: 1px solid var(--line);
  color: var(--text-main);
}

.leaderboard-table tr:hover td {
  background: rgba(255,255,255,0.02);
}

/* Empty States */
.empty-state {
  padding: 48px;
  text-align: center;
  border: 1px dashed var(--line-strong);
  border-radius: 24px;
  color: var(--text-soft);
  background: rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}
.empty-state:hover {
  background: rgba(0, 0, 0, 0.3);
  border-color: var(--accent);
}
.empty-title {
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 12px;
}
.empty-subtitle {
  font-size: 14px;
  line-height: 1.8;
  max-width: 400px;
  margin: 0 auto;
}

/* Chat Interface */
.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--line);
  background: rgba(0,0,0,0.2);
  border-radius: 20px 20px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chat-model-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
}
.chat-model-status {
  font-size: 13px;
}
.chat-history {
  padding: 24px;
  min-height: 400px;
  max-height: 600px;
  overflow-y: auto;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 15px;
}

/* Gradio Overrides */
#prompt-box textarea, #system-box textarea, #chat-input textarea {
  background: rgba(0, 0, 0, 0.2) !important;
  border: 1px solid var(--line) !important;
  color: #fff !important;
  border-radius: 16px !important;
  padding: 16px !important;
  font-size: 15px !important;
  transition: border-color 0.2s, box-shadow 0.2s;
}

#prompt-box textarea:focus, #system-box textarea:focus, #chat-input textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(93, 92, 255, 0.2) !important;
}

.gr-button-primary {
  background: var(--btn-gradient) !important;
  color: #fff !important;
  border: none !important;
  font-weight: 600 !important;
  border-radius: 12px !important;
  padding: 10px 24px !important;
  box-shadow: 0 4px 12px rgba(93, 92, 255, 0.3) !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
}

.gr-button-primary:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(93, 92, 255, 0.4) !important;
}

.gr-button-secondary {
  background: rgba(255, 255, 255, 0.05) !important;
  color: #fff !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  font-weight: 500 !important;
}

.gr-button-secondary:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}
"""
