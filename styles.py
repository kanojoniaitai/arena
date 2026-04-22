CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700;900&family=Noto+Serif+SC:wght@400;600;700&family=Fira+Code:wght@400;500;600&display=swap');

:root {
  --bg-base: #faf8f5;
  --bg-surface: #fffdf9;
  --bg-elevated: #f5f0ea;
  --bg-overlay: #ede7df;
  --bg-hover: #f0ebe4;
  --bg-active: #e8e0d6;
  --bg-input: #fffefb;
  --bg-card: #fffdf9;
  --bg-sidebar: #fffdf9;

  --border-subtle: rgba(139,90,43,0.06);
  --border-default: rgba(139,90,43,0.12);
  --border-strong: rgba(139,90,43,0.20);
  --border-accent: rgba(180,120,60,0.40);

  --text-primary: #2c1810;
  --text-secondary: #5c3d2e;
  --text-tertiary: #8b6f5e;
  --text-muted: #b09a8a;
  --text-placeholder: #b09a8a;

  --accent: #c47a3a;
  --accent-hover: #a8622a;
  --accent-dim: #8b4c1a;
  --accent-glow: rgba(196,122,58,0.20);
  --accent-subtle: rgba(196,122,58,0.08);
  --accent-bg: rgba(196,122,58,0.10);

  --green: #5a9e6f;
  --green-glow: rgba(90,158,111,0.20);
  --green-bg: rgba(90,158,111,0.10);
  --green-light: #e8f5e9;

  --amber: #d4943a;
  --amber-glow: rgba(212,148,58,0.20);
  --amber-bg: rgba(212,148,58,0.10);
  --amber-light: #fef3c7;

  --red: #c45a5a;
  --red-glow: rgba(196,90,90,0.20);
  --red-bg: rgba(196,90,90,0.10);
  --red-light: #fde8e8;

  --cyan: #5a9ea0;
  --cyan-bg: rgba(90,158,160,0.10);
  --cyan-light: #e0f2f1;

  --pink: #d4728c;
  --pink-bg: rgba(212,114,140,0.10);
  --pink-glow: rgba(212,114,140,0.15);

  --radius-xs: 6px;
  --radius-sm: 8px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 18px;
  --radius-full: 9999px;
  --shadow-sm: 0 1px 3px rgba(139,90,43,0.04), 0 1px 4px rgba(139,90,43,0.06);
  --shadow-md: 0 4px 8px rgba(139,90,43,0.05), 0 2px 10px rgba(139,90,43,0.08);
  --shadow-lg: 0 10px 20px rgba(139,90,43,0.05), 0 6px 14px rgba(139,90,43,0.08);
  --shadow-xl: 0 20px 40px rgba(139,90,43,0.06), 0 12px 28px rgba(139,90,43,0.10);

  --font-sans: 'Noto Sans SC',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  --font-serif: 'Noto Serif SC',Georgia,'Times New Roman',serif;
  --font-mono: 'Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;

  --sidebar-w: 280px;
  --header-h: 48px;
  --input-h: 110px;
  --transition-fast: 0.15s cubic-bezier(0.4,0,0.2,1);
  --transition-base: 0.25s cubic-bezier(0.4,0,0.2,1);
}

*,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }

html, body {
  height: 100% !important;
  overflow: hidden !important;
  background: var(--bg-base) !important;
  color: var(--text-primary) !important;
  font-family: var(--font-sans) !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body::before {
  content: '';
  position: fixed;
  top: -15%;
  left: 10%;
  width: 45%;
  height: 45%;
  background: radial-gradient(ellipse, rgba(196,122,58,0.05), transparent 70%);
  pointer-events: none;
  z-index: 0;
}

body::after {
  content: '';
  position: fixed;
  bottom: -15%;
  right: 8%;
  width: 40%;
  height: 40%;
  background: radial-gradient(ellipse, rgba(212,114,140,0.04), transparent 70%);
  pointer-events: none;
  z-index: 0;
}

.gradio-container {
  max-width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
  height: 100vh !important;
  overflow: hidden !important;
  position: relative;
  background: transparent !important;
}

.contain {
  height: 100vh !important;
  overflow: hidden !important;
  max-width: 100% !important;
  padding: 0 !important;
}

.main, .gap, .wrap {
  min-height: 0 !important;
}

.block {
  min-height: 0 !important;
}

#app-root, .gradio-container > .contain > .main {
  height: 100vh !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
}

.app-header {
  height: var(--header-h);
  min-height: var(--header-h);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-default);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
  position: relative;
  z-index: 100;
}

.app-header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent-glow), var(--pink-glow), transparent);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-logo {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--accent), var(--pink));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
  color: #fff;
  box-shadow: 0 0 12px var(--accent-glow);
}

.header-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.header-version {
  font-size: 9px;
  font-weight: 600;
  color: var(--accent-hover);
  background: var(--accent-bg);
  padding: 2px 6px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-accent);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 8px var(--green-glow);
  animation: pulse-dot 2s infinite;
}

.header-status-text {
  font-size: 10px;
  color: var(--text-tertiary);
  font-weight: 500;
}

.app-body {
  display: flex !important;
  flex: 1 !important;
  overflow: hidden !important;
  height: calc(100vh - var(--header-h)) !important;
  min-height: 0 !important;
  gap: 0 !important;
}

.app-body > div {
  min-height: 0 !important;
}

.app-sidebar {
  width: var(--sidebar-w) !important;
  min-width: var(--sidebar-w) !important;
  max-width: var(--sidebar-w) !important;
  background: var(--bg-surface);
  border-right: 1px solid var(--border-default);
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
  flex-shrink: 0 !important;
  flex-grow: 0 !important;
  padding: 0 !important;
}

.sidebar-scroll {
  flex: 1;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-height: 0 !important;
  max-height: calc(100vh - var(--header-h)) !important;
}

.sidebar-scroll::-webkit-scrollbar { width: 4px; }
.sidebar-scroll::-webkit-scrollbar-track { background: transparent; }
.sidebar-scroll::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 4px; }
.sidebar-scroll::-webkit-scrollbar-thumb:hover { background: var(--accent); }

.sidebar-section {
  margin-bottom: 10px;
}

.sidebar-section-title {
  font-size: 9px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 6px;
  padding: 0 2px;
}

.app-main {
  flex: 1 !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
  background: var(--bg-base);
  position: relative;
  min-width: 0 !important;
  padding: 0 !important;
}

.view-panel {
  flex: 1;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
  min-height: 0 !important;
  padding: 0 !important;
}

.main-content {
  flex: 1;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  padding: 14px 16px;
  min-height: 0 !important;
}

.main-content::-webkit-scrollbar { width: 5px; }
.main-content::-webkit-scrollbar-track { background: transparent; }
.main-content::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 5px; }
.main-content::-webkit-scrollbar-thumb:hover { background: var(--accent); }

.main-input-area {
  border-top: 1px solid var(--border-default);
  background: var(--bg-surface);
  padding: 10px 16px;
  flex-shrink: 0;
  position: relative;
}

.main-input-area::before {
  content: '';
  position: absolute;
  top: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent-glow), var(--pink-glow), transparent);
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.input-btn-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex !important;
  align-items: center;
  gap: 8px;
  padding: 8px 12px !important;
  border-radius: var(--radius-md) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  color: var(--text-secondary) !important;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent !important;
  user-select: none;
  background: transparent !important;
  margin-bottom: 2px;
}

.nav-item:hover {
  background: var(--bg-hover) !important;
  color: var(--text-primary) !important;
}

.nav-item.selected,
.nav-item[data-selected="true"] {
  background: var(--accent-bg) !important;
  color: var(--accent-hover) !important;
  border-color: var(--border-accent) !important;
}

.nav-icon {
  width: 18px;
  text-align: center;
  font-size: 14px;
  flex-shrink: 0;
}

.panel {
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  background: var(--bg-surface);
  padding: 14px;
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
}

.panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--pink), transparent);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-subtle);
}

.panel-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
  letter-spacing: -0.01em;
}

.panel-title-icon {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent-glow);
}

textarea,
.gr-text-input > textarea,
.gr-text-input > input,
#system-box textarea,
#chat-input textarea,
#chat-input-single textarea,
.gr-box textarea,
.gr-box input[type="text"] {
  background: var(--bg-input) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-md) !important;
  color: var(--text-primary) !important;
  font-size: 12px !important;
  font-family: var(--font-sans) !important;
  transition: all var(--transition-fast) !important;
  resize: none !important;
}

textarea:focus,
.gr-text-input > textarea:focus,
#system-box textarea:focus,
#chat-input textarea:focus,
#chat-input-single textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
  outline: none !important;
}

textarea::placeholder,
#system-box textarea::placeholder,
#chat-input textarea::placeholder,
#chat-input-single textarea::placeholder {
  color: var(--text-muted) !important;
}

input[type="number"],
.gr-number input {
  background: var(--bg-input) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-primary) !important;
  font-family: var(--font-mono) !important;
  font-size: 11px !important;
}

input[type="number"]:focus,
.gr-number input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

.gr-button {
  border-radius: var(--radius-md) !important;
  font-weight: 600 !important;
  font-size: 11px !important;
  font-family: var(--font-sans) !important;
  transition: all var(--transition-fast) !important;
  border: 1px solid transparent !important;
  cursor: pointer !important;
  padding: 6px 14px !important;
  white-space: nowrap !important;
}

.gr-button-primary {
  background: linear-gradient(135deg, var(--accent), var(--accent-dim)) !important;
  color: #fff !important;
  box-shadow: 0 2px 10px rgba(196,122,58,0.30) !important;
  border: none !important;
}
.gr-button-primary:hover {
  background: linear-gradient(135deg, var(--accent-hover), var(--accent)) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 18px rgba(196,122,58,0.40) !important;
}
.gr-button-primary:active { transform: translateY(0); }

.gr-button-secondary {
  background: var(--bg-elevated) !important;
  border-color: var(--border-default) !important;
  color: var(--text-secondary) !important;
}
.gr-button-secondary:hover {
  background: var(--bg-hover) !important;
  border-color: var(--border-strong) !important;
  color: var(--text-primary) !important;
}

.sidebar-btn-row {
  display: flex;
  gap: 4px;
}
.sidebar-btn-row .gr-button {
  flex: 1;
  padding: 5px 8px !important;
  font-size: 11px !important;
}

.model-grid, .result-grid {
  display: grid;
  gap: 8px;
}
.model-grid {
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}
.result-grid {
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
}

.model-card, .result-card {
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  padding: 10px;
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}

.model-card::before, .result-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--pink), transparent);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.model-card:hover, .result-card:hover {
  background: var(--bg-hover);
  border-color: var(--border-accent);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.model-card:hover::before, .result-card:hover::before { opacity: 1; }

.model-index {
  color: var(--text-muted);
  font-size: 8px;
  font-family: var(--font-mono);
  margin-bottom: 3px;
}

.model-name {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.model-path {
  color: var(--text-muted);
  font-size: 8px;
  font-family: var(--font-mono);
  word-break: break-all;
  line-height: 1.4;
  max-height: 24px;
  overflow: hidden;
}

.meta-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 6px;
  border-radius: var(--radius-full);
  font-size: 8px;
  font-weight: 600;
  font-family: var(--font-mono);
  background: var(--bg-overlay);
  border: 1px solid var(--border-subtle);
  margin-right: 2px;
  margin-bottom: 2px;
}

.meta-badge.params { color: var(--text-secondary); }
.meta-badge.quant { color: var(--cyan); background: var(--cyan-bg); border-color: rgba(90,158,160,0.15); }
.meta-badge.size { color: var(--green); background: var(--green-bg); border-color: rgba(90,158,111,0.15); }

.status-pill {
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 8px;
  font-weight: 600;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  letter-spacing: 0.02em;
}

.status-pill::before {
  content: '';
  width: 5px;
  height: 5px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.status-done { color: var(--green); background: var(--green-bg); border-color: rgba(90,158,111,0.15); }
.status-done::before { background: var(--green); box-shadow: 0 0 5px var(--green-glow); }

.status-generating { color: var(--accent-hover); background: var(--accent-subtle); border-color: var(--border-accent); }
.status-generating::before { background: var(--accent); animation: pulse-dot 1.5s infinite; }

.status-failed { color: var(--red); background: var(--red-bg); border-color: rgba(196,90,90,0.15); }
.status-failed::before { background: var(--red); }

.status-loading { color: var(--amber); background: var(--amber-bg); border-color: rgba(212,148,58,0.15); }
.status-loading::before { background: var(--amber); animation: pulse-dot 1.5s infinite; }

.status-waiting { color: var(--text-tertiary); background: var(--bg-overlay); border-color: var(--border-subtle); }
.status-waiting::before { background: var(--text-muted); }

/* GRADIO OVERRIDES FOR VERCEL/LINEAR LOOK */
#arena-chatbot {
  background: var(--bg-panel) !important;
  border: 1px solid var(--line) !important;
  border-radius: var(--radius-lg) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
#arena-chatbot .message-wrap {
  gap: 16px !important;
}
#arena-chatbot .message.user {
  background: rgba(59, 130, 246, 0.15) !important;
  border: 1px solid rgba(59, 130, 246, 0.3) !important;
  color: var(--text-main) !important;
}
#arena-chatbot .message.bot {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid var(--line) !important;
  color: var(--text-main) !important;
}
#arena-chatbot .prose pre {
  background: rgba(0, 0, 0, 0.5) !important;
  border: 1px solid var(--line) !important;
}

.msg-content pre {
  background: var(--bg-base) !important;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
  overflow-x: auto !important;
  margin: 4px 0;
  font-family: var(--font-mono);
  font-size: 10px;
  line-height: 1.5;
}

.msg-content code {
  font-family: var(--font-mono);
  font-size: 10px;
  background: var(--bg-overlay);
  padding: 1px 4px;
  border-radius: var(--radius-xs);
  color: var(--accent-hover);
}

.msg-content pre code {
  background: transparent;
  padding: 0;
  color: var(--text-primary);
}

.msg-content p { margin: 3px 0; }
.msg-content ul, .msg-content ol { margin: 3px 0; padding-left: 16px; }
.msg-content li { margin: 1px 0; }
.msg-content blockquote {
  border-left: 3px solid var(--accent);
  padding-left: 8px;
  margin: 4px 0;
  color: var(--text-tertiary);
}
.msg-content h1, .msg-content h2, .msg-content h3,
.msg-content h4, .msg-content h5, .msg-content h6 {
  color: var(--text-primary);
  margin: 6px 0 3px 0;
  font-weight: 700;
}
.msg-content table { border-collapse: collapse; width: 100%; margin: 4px 0; font-size: 11px; }
.msg-content th, .msg-content td { border: 1px solid var(--border-default); padding: 3px 6px; text-align: left; }
.msg-content th { background: var(--bg-overlay); font-weight: 600; }

.code-block-wrapper {
  margin: 4px 0;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg-base);
}

.code-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 3px 8px;
  background: var(--bg-overlay);
  border-bottom: 1px solid var(--border-subtle);
  font-size: 9px;
  font-family: var(--font-mono);
  color: var(--text-tertiary);
}

.copy-code-btn {
  background: var(--bg-hover);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xs);
  color: var(--text-secondary);
  font-size: 9px;
  padding: 2px 7px;
  cursor: pointer;
  font-family: var(--font-sans);
  transition: all var(--transition-fast);
}

.copy-code-btn:hover {
  background: var(--accent-bg);
  border-color: var(--border-accent);
  color: var(--accent-hover);
}

.empty-state {
  padding: 36px 24px;
  text-align: center;
  border: 2px dashed var(--border-strong);
  border-radius: var(--radius-xl);
  color: var(--text-tertiary);
  background: var(--bg-surface);
}

.empty-title {
  color: var(--text-secondary);
  font-weight: 700;
  font-size: 14px;
  margin-bottom: 4px;
}

.empty-subtitle {
  font-size: 11px;
  color: var(--text-muted);
}

/* Vercel Theme Specific Overrides */
body {
  background-color: var(--bg-main) !important;
  color: var(--text-main) !important;
}

.gradio-container {
  max-width: 1400px !important;
  padding: 0 !important;
}

.app-main {
  height: 100vh;
  display: flex;
}

.sidebar {
  background: var(--bg-panel);
  border-right: 1px solid var(--line);
  padding: 24px;
  height: 100vh;
  overflow-y: auto;
}

.main-content {
  padding: 32px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Buttons */
.gr-button {
  border-radius: 6px !important;
  font-weight: 500 !important;
}
.gr-button-primary {
  background: var(--text-main) !important;
  color: var(--bg-main) !important;
}
.gr-button-secondary {
  background: transparent !important;
  border: 1px solid var(--line) !important;
  color: var(--text-main) !important;
}

/* HTML Preview in Chatbot */
.message.bot .html-preview-btn {
    display: inline-block;
    margin-bottom: 12px;
    padding: 8px 16px;
    background-color: var(--text-main) !important;
    color: var(--bg-main) !important;
    border-radius: 6px;
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
}
.message.bot .html-preview-btn:hover {
    background-color: #e4e4e7 !important;
}
.html-preview-container {
  margin-bottom: 12px;
  padding: 10px;
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
  padding: 6px 12px;
  background: var(--text-main);
  color: var(--bg-main) !important;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
}
.html-preview-btn:hover {
  background: #e4e4e7;
  transform: translateY(-1px);
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 6px;
  margin-bottom: 10px;
}

.stat-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 8px;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.stat-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--pink));
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.stat-card:hover { border-color: var(--border-accent); background: var(--bg-hover); }
.stat-card:hover::after { opacity: 1; }

.stat-label {
  font-size: 8px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 16px;
  font-weight: 800;
  color: var(--text-primary);
  font-family: var(--font-mono);
  letter-spacing: -0.02em;
}

.stat-value.accent { color: var(--accent-hover); }
.stat-value.ok { color: var(--green); }
.stat-value.warn { color: var(--amber); }

.stat-delta {
  font-size: 9px;
  color: var(--text-muted);
  margin-top: 1px;
  font-family: var(--font-mono);
}

.compare-panel {
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 12px;
}

.compare-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-subtle);
}

.compare-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-primary);
}

.compare-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  border-bottom: 1px solid var(--border-subtle);
}

.compare-metric:last-child { border-bottom: none; }

.compare-metric-value {
  font-size: 10px;
  font-weight: 700;
  font-family: var(--font-mono);
}

.template-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3px;
}

.template-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  padding: 5px 7px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.template-card:hover {
  background: var(--bg-hover);
  border-color: var(--border-accent);
}

.template-card.active {
  background: var(--accent-bg);
  border-color: var(--border-accent);
}

.template-name {
  font-size: 9px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1px;
}

.template-desc {
  font-size: 7px;
  color: var(--text-muted);
  line-height: 1.3;
}

.progress-bar {
  width: 100%;
  height: 2px;
  background: var(--bg-overlay);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 3px;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--pink));
  border-radius: 2px;
  transition: width 0.3s ease;
}

.leaderboard-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 11px;
}

.leaderboard-table th {
  text-align: left;
  padding: 6px 8px;
  color: var(--text-muted);
  font-weight: 600;
  font-size: 8px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border-bottom: 1px solid var(--border-default);
  background: var(--bg-overlay);
  position: sticky;
  top: 0;
  z-index: 1;
}

.leaderboard-table th:first-child { border-radius: var(--radius-sm) 0 0 0; }
.leaderboard-table th:last-child { border-radius: 0 var(--radius-sm) 0 0; }

.leaderboard-table td {
  padding: 5px 8px;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  vertical-align: middle;
}

.leaderboard-table tr:hover td {
  background: var(--bg-hover);
}

.winner-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  font-weight: 700;
  color: var(--amber);
  background: var(--amber-bg);
  padding: 2px 7px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(212,148,58,0.15);
}

.export-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-secondary) !important;
  font-size: 10px;
  font-weight: 600;
  font-family: var(--font-sans);
  text-decoration: none;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.export-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-accent);
  color: var(--accent-hover) !important;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  color: var(--text-tertiary);
  font-size: 10px;
}

.typing-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  animation: typing-bounce 1.4s infinite ease-in-out;
}
.typing-dot:nth-child(2) { animation-delay: 0.16s; }
.typing-dot:nth-child(3) { animation-delay: 0.32s; }

.status-text {
  font-size: 10px !important;
  color: var(--text-tertiary) !important;
}

.status-text p {
  font-size: 10px !important;
  color: var(--text-tertiary) !important;
}

.gr-accordion {
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-md) !important;
  background: var(--bg-elevated) !important;
}

.gr-accordion .label-wrap {
  font-size: 11px !important;
  font-weight: 600 !important;
  color: var(--text-secondary) !important;
}

.gr-checkboxgroup {
  gap: 2px !important;
  max-height: 200px !important;
  overflow-y: auto !important;
  padding-right: 4px !important;
}

.gr-checkboxgroup::-webkit-scrollbar { width: 3px; }
.gr-checkboxgroup::-webkit-scrollbar-track { background: transparent; }
.gr-checkboxgroup::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 3px; }

.gr-checkboxgroup label {
  font-size: 10px !important;
  padding: 2px 4px !important;
  border-radius: var(--radius-xs) !important;
  transition: background var(--transition-fast) !important;
}

.gr-checkboxgroup label:hover {
  background: var(--bg-hover) !important;
}

.gr-dropdown {
  font-size: 11px !important;
}

.gr-slider {
  margin: 2px 0 !important;
}

.gr-slider .head {
  font-size: 10px !important;
  color: var(--text-secondary) !important;
}

.gr-slider input[type="range"] {
  height: 3px !important;
}

.gr-radio-group {
  gap: 0 !important;
}

.gr-radio-group label {
  font-size: 11px !important;
  padding: 4px 8px !important;
  border-radius: var(--radius-sm) !important;
  transition: all var(--transition-fast) !important;
}

.gr-markdown {
  font-size: 11px !important;
}

.gr-markdown p {
  font-size: 11px !important;
  color: var(--text-secondary) !important;
  line-height: 1.5 !important;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px currentColor; }
  50% { opacity: 0.5; box-shadow: 0 0 3px currentColor; }
}

@keyframes msg-in {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes typing-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1.1); opacity: 1; }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes cute-bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.view-fade-in {
  animation: fade-in 0.2s ease-out;
}

.single-chat-wrapper {
  display: flex;
  flex-direction: column;
  height: calc(100vh - var(--header-h) - var(--input-h) - 50px);
  min-height: 300px;
}

.single-chat-wrapper .chat-col-card {
  height: 100% !important;
  max-height: none !important;
}

.bench-info {
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  margin-bottom: 12px;
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.bench-info strong {
  color: var(--amber);
}

.lb-actions {
  display: flex;
  gap: 6px;
  padding: 8px 0;
}

.bench-actions {
  display: flex;
  gap: 6px;
  padding: 8px 0;
}

.gr-column > .gap:has(> .empty:only-child) {
  flex: 1;
}
"""
