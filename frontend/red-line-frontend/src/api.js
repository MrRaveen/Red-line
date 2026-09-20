/**
 * RED-LINE — Shared JS utilities (React port of app.js)
 * auth, API helpers, formatting helpers
 * (No JSX here — see badges.jsx for JSX badge components)
 */

export const API_BASE = 'http://localhost:8001/api/dashboard';

// ── Auth helpers ──────────────────────────────────────────────
export const Auth = {
  get userID()  { return localStorage.getItem('rl_userID') || ''; },
  get email()   { return localStorage.getItem('rl_email')  || ''; },
  set(uid, em)  { localStorage.setItem('rl_userID', uid); localStorage.setItem('rl_email', em); },
  clear()       { localStorage.removeItem('rl_userID'); localStorage.removeItem('rl_email'); },
  isLoggedIn()  { return !!this.userID; },
};

// ── Fetch wrapper ─────────────────────────────────────────────
export async function api(path, opts = {}) {
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

// ── Formatting helpers ────────────────────────────────────────
export function fmtDate(iso) {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('en-US', { month:'short', day:'numeric', year:'numeric', hour:'2-digit', minute:'2-digit' });
  } catch { return iso; }
}

export function fmtRelative(iso) {
  if (!iso) return '—';
  const diff = Date.now() - new Date(iso).getTime();
  const s = Math.floor(diff / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s/60)}m ago`;
  if (s < 86400) return `${Math.floor(s/3600)}h ago`;
  return `${Math.floor(s/86400)}d ago`;
}

// ── Attack-type colour map ────────────────────────────────────
export const TYPE_COLORS = {
  'prompt injection':        '#00bcd4',
  'halusination attack':     '#7c5cbf',
  'PII exfilteration attack':'#ffb300',
  'jailbreak attack':        '#ff4444',
  'all':                     '#00ff88',
};
export function typeColor(t) { return TYPE_COLORS[t] || '#8c9db5'; }

// ── Severity helpers ──────────────────────────────────────────
export function severityPct(s) {
  return { NONE:0, LOW:25, MEDIUM:50, HIGH:75, CRITICAL:100 }[s] || 0;
}

export function severityClass(s) {
  return { NONE:'low', LOW:'low', MEDIUM:'medium', HIGH:'high', CRITICAL:'critical' }[s] || 'low';
}

export function escHtml(str) {
  return String(str || '');
}
