#!/usr/bin/env python3
"""
Blind XSS Dorking Tool - Flask Web Server
Usage: python blindxss_web.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Dork Categories
# ──────────────────────────────────────────────────────────────────────────────
DORK_CATEGORIES = {
    "Generic Contact Forms": {
        "icon": "📬",
        "dorks": [
            'site:%s inurl:contact',
            'site:%s inurl:contact-us',
            'site:%s inurl:contactus',
            'site:%s inurl:contact_us',
            'site:%s intitle:"contact us"',
            'site:%s intitle:"contact" inurl:form',
            'site:%s "contact form" inurl:php',
            'site:%s inurl:reach-us',
            'site:%s inurl:get-in-touch',
            'site:%s inurl:write-to-us',
        ],
    },
    "Feedback & Comment Forms": {
        "icon": "📝",
        "dorks": [
            'site:%s inurl:feedback',
            'site:%s inurl:feedback-form',
            'site:%s intitle:"feedback" inurl:form',
            'site:%s inurl:comment inurl:form',
            'site:%s inurl:comments',
            'site:%s "leave a comment" OR "post a comment"',
            'site:%s inurl:review inurl:form',
            'site:%s inurl:testimonial inurl:form',
        ],
    },
    "Login & Registration Forms": {
        "icon": "🔐",
        "dorks": [
            'site:%s inurl:login',
            'site:%s inurl:signin',
            'site:%s inurl:register',
            'site:%s inurl:signup',
            'site:%s inurl:account/create',
            'site:%s inurl:user/register',
            'site:%s inurl:join',
            'site:%s intitle:"create account"',
            'site:%s intitle:"sign up" inurl:form',
        ],
    },
    "Search Boxes": {
        "icon": "🔍",
        "dorks": [
            'site:%s inurl:search',
            'site:%s inurl:q= OR inurl:query= OR inurl:s=',
            'site:%s intitle:"search" inurl:search',
            'site:%s inurl:find',
            'site:%s inurl:lookup',
        ],
    },
    "Support & Help Desk": {
        "icon": "💬",
        "dorks": [
            'site:%s inurl:support',
            'site:%s inurl:helpdesk',
            'site:%s inurl:help inurl:form',
            'site:%s inurl:ticket',
            'site:%s inurl:submit-ticket',
            'site:%s inurl:open-ticket',
            'site:%s intitle:"submit a request"',
            'site:%s intitle:"help desk"',
        ],
    },
    "Survey & Poll Forms": {
        "icon": "📊",
        "dorks": [
            'site:%s inurl:survey',
            'site:%s inurl:poll',
            'site:%s inurl:questionnaire',
            'site:%s intitle:"survey" inurl:form',
            'site:%s inurl:quiz',
        ],
    },
    "Order & Checkout Forms": {
        "icon": "📦",
        "dorks": [
            'site:%s inurl:order',
            'site:%s inurl:checkout',
            'site:%s inurl:cart',
            'site:%s inurl:purchase',
            'site:%s inurl:buy',
            'site:%s inurl:payment',
            'site:%s intitle:"order form"',
        ],
    },
    "Newsletter & Subscribe": {
        "icon": "📋",
        "dorks": [
            'site:%s inurl:subscribe',
            'site:%s inurl:newsletter',
            'site:%s inurl:mailing-list',
            'site:%s intitle:"subscribe" inurl:form',
            'site:%s "subscribe to our newsletter"',
        ],
    },
    "Profile & Account Forms": {
        "icon": "🧑‍💼",
        "dorks": [
            'site:%s inurl:profile',
            'site:%s inurl:account/edit',
            'site:%s inurl:settings',
            'site:%s inurl:update-profile',
            'site:%s inurl:my-account',
            'site:%s inurl:dashboard',
        ],
    },
    "Upload & File Submission": {
        "icon": "📤",
        "dorks": [
            'site:%s inurl:upload',
            'site:%s inurl:file-upload',
            'site:%s inurl:submit',
            'site:%s inurl:submission',
            'site:%s intitle:"upload" inurl:form',
            'site:%s inurl:apply',
        ],
    },
    "Job & Career Applications": {
        "icon": "💼",
        "dorks": [
            'site:%s inurl:careers',
            'site:%s inurl:jobs',
            'site:%s inurl:apply',
            'site:%s intitle:"job application"',
            'site:%s inurl:recruitment',
            'site:%s inurl:vacancy',
        ],
    },
    "Admin & Backend Panels": {
        "icon": "⚙️",
        "dorks": [
            'site:%s inurl:admin',
            'site:%s inurl:wp-admin',
            'site:%s inurl:administrator',
            'site:%s inurl:cpanel',
            'site:%s inurl:phpmyadmin',
            'site:%s intitle:"admin panel"',
            'site:%s inurl:manage',
            'site:%s inurl:portal',
        ],
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# HTML Template
# ──────────────────────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>BlindXSS Dorker</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet"/>
<style>
  :root {
    --bg:        #050a0e;
    --bg2:       #0a1520;
    --bg3:       #0d1f2d;
    --accent:    #00ff9d;
    --accent2:   #00c8ff;
    --accent3:   #ff3c6e;
    --dim:       #1a3a4a;
    --text:      #b8e4f0;
    --text-dim:  #4a7a8a;
    --border:    #1e4a5c;
    --glow:      0 0 20px rgba(0,255,157,0.3);
    --glow2:     0 0 20px rgba(0,200,255,0.3);
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    min-height: 100vh;
    overflow-x: hidden;
    position: relative;
  }

  /* Scanline overlay */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.08) 2px,
      rgba(0,0,0,0.08) 4px
    );
    pointer-events: none;
    z-index: 100;
  }

  /* Grid background */
  body::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,255,157,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,255,157,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  .container {
    max-width: 960px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
    position: relative;
    z-index: 1;
  }

  /* ── Header ── */
  header {
    text-align: center;
    padding: 3rem 0 2.5rem;
    position: relative;
  }

  .logo-line {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.8rem, 5vw, 3.2rem);
    font-weight: 900;
    letter-spacing: 0.12em;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none;
    filter: drop-shadow(0 0 18px rgba(0,255,157,0.5));
    animation: flicker 6s infinite;
  }

  @keyframes flicker {
    0%,95%,100% { opacity: 1; }
    96% { opacity: 0.85; }
    97% { opacity: 1; }
    98% { opacity: 0.7; }
    99% { opacity: 1; }
  }

  .logo-sub {
    font-size: 0.75rem;
    letter-spacing: 0.4em;
    color: var(--text-dim);
    margin-top: 0.5rem;
    text-transform: uppercase;
  }

  .badge-row {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1.2rem;
    flex-wrap: wrap;
  }

  .badge {
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    padding: 0.25rem 0.7rem;
    border: 1px solid var(--border);
    color: var(--text-dim);
    text-transform: uppercase;
  }

  /* ── Input Section ── */
  .search-wrap {
    background: var(--bg2);
    border: 1px solid var(--border);
    padding: 2rem;
    margin-bottom: 2rem;
    position: relative;
    clip-path: none;
  }

  .search-wrap::before {
    content: '// TARGET ACQUISITION';
    position: absolute;
    top: -0.6rem;
    left: 1.5rem;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    color: var(--accent);
    background: var(--bg2);
    padding: 0 0.5rem;
  }

  .input-row {
    display: flex;
    gap: 0.75rem;
    align-items: stretch;
  }

  .input-prefix {
    display: flex;
    align-items: center;
    color: var(--accent2);
    font-size: 1rem;
    white-space: nowrap;
    padding: 0 0.5rem;
    border: 1px solid var(--border);
    background: var(--bg3);
    border-right: none;
  }

  #url-input {
    flex: 1;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-left: none;
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    font-size: 1rem;
    padding: 0.75rem 1rem;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
    caret-color: var(--accent2);
  }

  #url-input::placeholder { color: #5f8b9a; }

  #url-input:focus {
    border-color: var(--accent2);
    background: #0e2430;
    box-shadow: 0 0 0 2px rgba(0,200,255,0.18);
  }

  #url-input:-webkit-autofill,
  #url-input:-webkit-autofill:hover,
  #url-input:-webkit-autofill:focus {
    -webkit-text-fill-color: var(--text);
    -webkit-box-shadow: 0 0 0 1000px var(--bg3) inset;
  }

  #scan-btn {
    background: transparent;
    border: 1px solid var(--accent);
    color: var(--accent);
    font-family: 'Orbitron', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    padding: 0.75rem 1.5rem;
    cursor: pointer;
    text-transform: uppercase;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
    white-space: nowrap;
  }

  #scan-btn::before {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--accent);
    transform: translateX(-100%);
    transition: transform 0.2s;
    z-index: -1;
  }

  #scan-btn:hover {
    color: var(--bg);
    box-shadow: var(--glow);
  }

  #scan-btn:hover::before { transform: translateX(0); }

  #scan-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  /* ── Stats Bar ── */
  #stats-bar {
    display: none;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding: 0.75rem 1rem;
    background: var(--bg2);
    border: 1px solid var(--border);
    font-size: 0.75rem;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .stat-item { color: var(--text-dim); }
  .stat-item span { color: var(--accent); font-weight: bold; }

  #copy-all-btn {
    background: transparent;
    border: 1px solid var(--accent2);
    color: var(--accent2);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    padding: 0.35rem 0.8rem;
    cursor: pointer;
    text-transform: uppercase;
    transition: all 0.2s;
  }

  #copy-all-btn:hover {
    background: var(--accent2);
    color: var(--bg);
  }

  /* ── Category Blocks ── */
  #results { display: none; }

  .category-block {
    margin-bottom: 1.5rem;
    border: 1px solid var(--border);
    background: var(--bg2);
    animation: slideIn 0.3s ease both;
  }

  @keyframes slideIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .cat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 1rem;
    background: var(--bg3);
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    user-select: none;
    transition: background 0.15s;
  }

  .cat-header:hover { background: var(--dim); }

  .cat-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    color: var(--accent2);
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .cat-icon { font-size: 1rem; }

  .cat-count {
    font-size: 0.65rem;
    color: var(--text-dim);
    letter-spacing: 0.1em;
  }

  .cat-toggle {
    color: var(--text-dim);
    font-size: 0.8rem;
    transition: transform 0.2s;
  }

  .cat-toggle.open { transform: rotate(180deg); }

  .dork-list {
    list-style: none;
    overflow: hidden;
    max-height: 2000px;
    transition: max-height 0.3s ease;
  }

  .dork-list.collapsed { max-height: 0; }

  .dork-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 1rem;
    border-bottom: 1px solid rgba(30,74,92,0.4);
    cursor: pointer;
    transition: background 0.15s;
    text-decoration: none;
    color: inherit;
  }

  .dork-item:last-child { border-bottom: none; }

  .dork-item:hover {
    background: rgba(0,255,157,0.05);
  }

  .dork-item:hover .dork-text { color: var(--accent); }
  .dork-item:hover .open-icon { opacity: 1; color: var(--accent); }

  .line-num {
    color: var(--text-dim);
    font-size: 0.65rem;
    min-width: 2rem;
    text-align: right;
    opacity: 0.6;
  }

  .dork-text {
    flex: 1;
    font-size: 0.8rem;
    color: var(--text);
    transition: color 0.15s;
    word-break: break-all;
  }

  .dork-text .kw-site  { color: var(--accent3); }
  .dork-text .kw-inurl { color: var(--accent2); }
  .dork-text .kw-intitle { color: #ffcc00; }
  .dork-text .kw-domain { color: var(--accent); }

  .open-icon {
    font-size: 0.75rem;
    color: var(--text-dim);
    opacity: 0.4;
    transition: opacity 0.15s, color 0.15s;
    white-space: nowrap;
  }

  /* ── Loading ── */
  #loader {
    display: none;
    text-align: center;
    padding: 2rem;
    color: var(--accent);
    font-size: 0.85rem;
    letter-spacing: 0.2em;
    animation: pulse 1s infinite;
  }

  @keyframes pulse {
    0%,100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  /* ── Error ── */
  #error-box {
    display: none;
    padding: 1rem;
    border: 1px solid var(--accent3);
    background: rgba(255,60,110,0.08);
    color: var(--accent3);
    font-size: 0.8rem;
    margin-bottom: 1.5rem;
  }

  /* ── Toast ── */
  #toast {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: var(--bg3);
    border: 1px solid var(--accent);
    color: var(--accent);
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    padding: 0.6rem 1.2rem;
    z-index: 200;
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.3s;
    pointer-events: none;
  }

  #toast.show { opacity: 1; transform: translateY(0); }

  /* ── Footer ── */
  footer {
    text-align: center;
    padding: 2rem 0 1rem;
    color: var(--text-dim);
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
  }

  /* ── Responsive ── */
  @media (max-width: 600px) {
    .input-row { flex-direction: column; }
    .input-prefix { border-right: 1px solid var(--border); border-bottom: none; }
    #url-input { border-left: 1px solid var(--border); }
  }
</style>
</head>
<body>

<div class="container">

  <!-- Header -->
  <header>
    <div class="logo-line">BLIND XSS DORKER</div>
    <div class="logo-sub">Google Dork Generator for Input Surface Discovery</div>
    <div class="logo-sub" style="margin-top:0.3rem;color:#00ff9d;opacity:0.6;">made by someonenamenicky</div>
    <div class="badge-row">
      <span class="badge">Recon</span>
      <span class="badge">Bug Bounty</span>
      <span class="badge">XSS Surface Mapping</span>
      <span class="badge">OSINT</span>
    </div>
  </header>

  <!-- Input -->
  <div class="search-wrap">
    <div class="input-row">
      <div class="input-prefix">target://</div>
      <input id="url-input" type="text" placeholder="nasa.gov" autocomplete="off" spellcheck="false"/>
      <button id="scan-btn" onclick="runScan()">⚡ SCAN</button>
    </div>
  </div>

  <!-- Error -->
  <div id="error-box"></div>

  <!-- Loader -->
  <div id="loader">[ GENERATING DORK STRINGS... ]</div>

  <!-- Stats Bar -->
  <div id="stats-bar">
    <div class="stat-item">TARGET: <span id="stat-target">—</span></div>
    <div class="stat-item">CATEGORIES: <span id="stat-cats">—</span></div>
    <div class="stat-item">TOTAL DORKS: <span id="stat-total">—</span></div>
    <button id="copy-all-btn" onclick="copyAll()">⎘ COPY ALL</button>
  </div>

  <!-- Results -->
  <div id="results"></div>

</div>

<!-- Toast -->
<div id="toast"></div>

<!-- Footer -->
<footer>
  FOR AUTHORIZED SECURITY RESEARCH &amp; BUG BOUNTY USE ONLY &nbsp;|&nbsp; ALWAYS OBTAIN PERMISSION BEFORE TESTING
</footer>

<script>
let allDorks = [];

function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function highlightDork(dork) {
  return dork
    .replace(/(site:)/g,        '<span class="kw-site">$1</span>')
    .replace(/(inurl:)/g,       '<span class="kw-inurl">$1</span>')
    .replace(/(intitle:)/g,     '<span class="kw-intitle">$1</span>')
    .replace(/site:[^\\s]+/,     m => {
      const parts = m.split(':');
      return '<span class="kw-site">site:</span><span class="kw-domain">' + escapeHtml(parts.slice(1).join(':')) + '</span>';
    });
}

function buildGoogleUrl(dork) {
  return 'https://www.google.com/search?q=' + encodeURIComponent(dork);
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}

async function runScan() {
  const raw = document.getElementById('url-input').value.trim();
  if (!raw) {
    showError('Please enter a target domain.');
    return;
  }

  clearError();
  document.getElementById('results').style.display = 'none';
  document.getElementById('stats-bar').style.display = 'none';
  document.getElementById('loader').style.display = 'block';
  document.getElementById('scan-btn').disabled = true;
  allDorks = [];

  try {
    const resp = await fetch('/dork', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: raw }),
    });
    const data = await resp.json();

    if (!resp.ok || data.error) {
      showError(data.error || 'Server error.');
      return;
    }

    renderResults(data);
  } catch(e) {
    showError('Request failed: ' + e.message);
  } finally {
    document.getElementById('loader').style.display = 'none';
    document.getElementById('scan-btn').disabled = false;
  }
}

function renderResults(data) {
  const container = document.getElementById('results');
  container.innerHTML = '';
  let totalCount = 0;

  data.categories.forEach((cat, ci) => {
    const block = document.createElement('div');
    block.className = 'category-block';
    block.style.animationDelay = (ci * 0.05) + 's';

    const header = document.createElement('div');
    header.className = 'cat-header';
    header.innerHTML = `
      <div class="cat-title">
        <span class="cat-icon">${cat.icon}</span>
        ${escapeHtml(cat.name)}
      </div>
      <div style="display:flex;align-items:center;gap:1rem;">
        <span class="cat-count">${cat.dorks.length} dork${cat.dorks.length!==1?'s':''}</span>
        <span class="cat-toggle open">▾</span>
      </div>`;

    const list = document.createElement('ul');
    list.className = 'dork-list';

    cat.dorks.forEach((dork, di) => {
      allDorks.push(dork);
      const googleUrl = buildGoogleUrl(dork);

      const item = document.createElement('a');
      item.className = 'dork-item';
      item.href = googleUrl;
      item.target = '_blank';
      item.rel = 'noopener noreferrer';
      item.title = 'Click to open in Google Search';
      item.innerHTML = `
        <span class="line-num">${String(di+1).padStart(2,'0')}</span>
        <span class="dork-text">${highlightDork(escapeHtml(dork))}</span>
        <span class="open-icon">↗ SEARCH</span>`;

      list.appendChild(item);
      totalCount++;
    });

    header.addEventListener('click', () => {
      const isOpen = !list.classList.contains('collapsed');
      list.classList.toggle('collapsed', isOpen);
      header.querySelector('.cat-toggle').classList.toggle('open', !isOpen);
    });

    block.appendChild(header);
    block.appendChild(list);
    container.appendChild(block);
  });

  // Stats
  document.getElementById('stat-target').textContent  = data.target;
  document.getElementById('stat-cats').textContent    = data.categories.length;
  document.getElementById('stat-total').textContent   = totalCount;
  document.getElementById('stats-bar').style.display  = 'flex';
  container.style.display = 'block';
}

function copyAll() {
  const text = allDorks.join('\\n');
  navigator.clipboard.writeText(text).then(() => {
    showToast('✓ ' + allDorks.length + ' DORKS COPIED TO CLIPBOARD');
  }).catch(() => {
    showToast('⚠ CLIPBOARD ACCESS DENIED');
  });
}

function showError(msg) {
  const el = document.getElementById('error-box');
  el.textContent = '⚠ ERROR: ' + msg;
  el.style.display = 'block';
}

function clearError() {
  document.getElementById('error-box').style.display = 'none';
}

// Allow Enter key
document.getElementById('url-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') runScan();
});
</script>
</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/dork", methods=["POST"])
def dork():
    data = request.get_json(force=True)
    raw = (data.get("url") or "").strip().lower()

    if not raw:
        return jsonify({"error": "No URL provided."}), 400

    # Strip protocol / www
    for prefix in ("https://", "http://", "www."):
        if raw.startswith(prefix):
            raw = raw[len(prefix):]
    target = raw.rstrip("/")

    if not target or "." not in target:
        return jsonify({"error": "Please enter a valid domain (e.g. nasa.gov)."}), 400

    categories = []
    for name, meta in DORK_CATEGORIES.items():
        filled = [d % target for d in meta["dorks"]]
        categories.append({
            "name": name,
            "icon": meta["icon"],
            "dorks": filled,
        })

    return jsonify({"target": target, "categories": categories})


if __name__ == "__main__":
    print("  BlindXSS Dorker Web Server")
    print("  ─────────────────────────────────────────")
    print("  Open: http://localhost:5000\n")
    app.run(debug=False, host="0.0.0.0", port=5000)
