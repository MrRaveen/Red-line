/**
 * RED-LINE — Shared JS utilities
 * auth, API helpers, toast, tab switching
 */

const API_BASE = 'http://localhost:8001/api/dashboard'; // ← change if SAGA API is on a different port

// ── Auth helpers ──────────────────────────────────────────────
const Auth = {
  get userID()   { return localStorage.getItem('rl_userID') || ''; },
  get email()    { return localStorage.getItem('rl_email')  || ''; },
  set(uid, em)   { localStorage.setItem('rl_userID', uid); localStorage.setItem('rl_email', em); },
  clear()        { localStorage.removeItem('rl_userID'); localStorage.removeItem('rl_email'); },
  isLoggedIn()   { return !!this.userID; },
  require()      { if (!this.isLoggedIn()) { window.location = 'index.html'; } },
};

// ── Fetch wrapper ─────────────────────────────────────────────
async function api(path, opts = {}) {
  const url     = API_BASE + path;
  const headers = { 'Content-Type': 'application/json' };
  if (Auth.userID) headers['X-User-ID'] = Auth.userID;
  if (opts.body && typeof opts.body === 'object') opts.body = JSON.stringify(opts.body);
  const res = await fetch(url, { ...opts, headers: { ...headers, ...(opts.headers || {}) } });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || res.statusText);
  }
  return res.json();
}

// ── Toast notifications ───────────────────────────────────────
const Toast = {
  container: null,
  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },
  show(message, type = 'info') {
    this.init();
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = message;
    this.container.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; el.style.transform = 'translateX(100%)'; el.style.transition = '0.3s'; setTimeout(() => el.remove(), 300); }, 3500);
  },
  success(m) { this.show(m, 'success'); },
  error(m)   { this.show(m, 'error');   },
  info(m)    { this.show(m, 'info');    },
};

// ── Tab switching ─────────────────────────────────────────────
function initTabs(containerSelector) {
  const container = document.querySelector(containerSelector || '.tabs');
  if (!container) return;
  container.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.toggle('active', p.id === target));
    });
  });
}

// ── Shared UI helpers ─────────────────────────────────────────
function initThemeToggle() {
  // Check local storage for theme
  const currentTheme = localStorage.getItem('rl_theme') || 'dark';
  document.documentElement.dataset.theme = currentTheme;

  // Append a toggle button to the topbar-actions if it exists
  const topbarActions = document.querySelector('.topbar-actions');
  if (topbarActions) {
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-outline';
    btn.style.marginLeft = '10px';
    btn.innerHTML = currentTheme === 'light' ? 'Dark Mode' : 'Light Mode';
    btn.onclick = () => {
      const theme = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
      document.documentElement.dataset.theme = theme;
      localStorage.setItem('rl_theme', theme);
      btn.innerHTML = theme === 'light' ? 'Dark Mode' : 'Light Mode';
    };
    topbarActions.insertBefore(btn, topbarActions.firstChild);
  }
}

async function deleteJob(jobId) {
  if (!confirm('Are you sure you want to delete this job and all its data? This action cannot be undone.')) return;
  try {
    await api(`/jobs/${jobId}`, { method: 'DELETE' });
    Toast.success('Job deleted successfully');
    // Reload the relevant page view
    if (typeof loadDashboard === 'function') {
      loadDashboard();
    } else if (typeof loadProjects === 'function') {
      loadProjects();
    } else {
      window.location = 'dashboard.html';
    }
  } catch (err) {
    Toast.error('Failed to delete job: ' + err.message);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
});

// ── Formatting helpers ────────────────────────────────────────
function fmtDate(iso) {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('en-US', { month:'short', day:'numeric', year:'numeric', hour:'2-digit', minute:'2-digit' });
  } catch { return iso; }
}

function fmtRelative(iso) {
  if (!iso) return '—';
  const diff = Date.now() - new Date(iso).getTime();
  const s = Math.floor(diff / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s/60)}m ago`;
  if (s < 86400) return `${Math.floor(s/3600)}h ago`;
  return `${Math.floor(s/86400)}d ago`;
}

function jobTypeBadge(type) {
  if (!type) return '<span class="badge badge-gray">—</span>';
  const map = {
    'prompt injection':       'badge-blue',
    'halusination attack':    'badge-purple',
    'PII exfilteration attack':'badge-yellow',
    'jailbreak attack':       'badge-red',
  };
  const cls = map[type] || 'badge-gray';
  return `<span class="badge ${cls}">${type}</span>`;
}

function statusBadge(status) {
  if (status === 'FINISHED') return '<span class="badge badge-green">FINISHED</span>';
  return '<span class="badge badge-yellow">PROCESSING</span>';
}

function severityBadge(sev) {
  const map = { NONE:'badge-gray', LOW:'badge-green', MEDIUM:'badge-yellow', HIGH:'badge-red', CRITICAL:'badge-red' };
  return `<span class="badge ${map[sev] || 'badge-gray'} severity-${sev}">${sev || 'NONE'}</span>`;
}

// ── Sidebar active link ───────────────────────────────────────
function markActiveSidebarLink() {
  const page = window.location.pathname.split('/').pop();
  document.querySelectorAll('.nav-link[data-page]').forEach(el => {
    el.classList.toggle('active', el.dataset.page === page);
  });
}

// ── Logout ────────────────────────────────────────────────────
function logout() {
  Auth.clear();
  window.location = 'index.html';
}

// ── Sidebar user display ──────────────────────────────────────
function renderSidebarUser() {
  const uid = Auth.userID;
  const el = document.getElementById('sidebar-username');
  if (el) el.textContent = uid;
  const av = document.getElementById('sidebar-avatar');
  if (av) av.textContent = uid ? uid[0].toUpperCase() : '?';
}

// ── Chart.js default style ────────────────────────────────────
function applyChartDefaults() {
  if (typeof Chart === 'undefined') return;
  Chart.defaults.color = '#8c9db5';
  Chart.defaults.borderColor = '#1e2d4a';
  Chart.defaults.font.family = "'Inter', sans-serif";
}

// ── Attack-type colour map ────────────────────────────────────
const TYPE_COLORS = {
  'prompt injection':        '#00bcd4',
  'halusination attack':     '#7c5cbf',
  'PII exfilteration attack':'#ffb300',
  'jailbreak attack':        '#ff4444',
  'all':                     '#00ff88',
};
function typeColor(t) { return TYPE_COLORS[t] || '#8c9db5'; }

// ── Verdict / severity → percentage for risk bar ──────────────
function severityPct(s) {
  return { NONE:0, LOW:25, MEDIUM:50, HIGH:75, CRITICAL:100 }[s] || 0;
}

function severityClass(s) {
  return { NONE:'low', LOW:'low', MEDIUM:'medium', HIGH:'high', CRITICAL:'critical' }[s] || 'low';
}
