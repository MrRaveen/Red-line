import { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import {
  Chart as ChartJS,
  ArcElement, BarElement,
  CategoryScale, LinearScale,
  Tooltip, Legend,
} from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import Sidebar from '../components/Sidebar';
import ThemeToggle from '../components/ThemeToggle';
import {
  api, API_BASE, fmtDate,
  severityPct, severityClass,
} from '../api';
import { jobTypeBadge, statusBadge, severityBadge } from '../badges.jsx';
import { useToast } from '../ToastContext';

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);
ChartJS.defaults.color = '#8c9db5';
ChartJS.defaults.borderColor = '#1e2d4a';
ChartJS.defaults.font.family = "'Inter', sans-serif";

// ── Helper ────────────────────────────────────────────────────
function escHtml(str) { return String(str || ''); }

// ── Sub-components ────────────────────────────────────────────

function ReportTab({ jobID }) {
  const toast = useToast();
  const [state, setState] = useState('loading'); // 'loading' | 'not-ready' | 'ready'
  const [report, setReport] = useState(null);
  const [allAttempts, setAllAttempts] = useState([]);
  const [filteredAttempts, setFilteredAttempts] = useState([]);
  const [searchQ, setSearchQ] = useState('');
  const [breachFilter, setBreachFilter] = useState('');

  const load = useCallback(async () => {
    setState('loading');
    try {
      const r = await api(`/jobs/${jobID}/report`);
      setReport(r);
      const attempts = r.attempts || [];
      setAllAttempts(attempts);
      setFilteredAttempts(attempts);
      setState('ready');
    } catch (e) {
      if (e.message.includes('404') || e.message.includes('not ready')) {
        setState('not-ready');
      } else {
        toast.error('Report error: ' + e.message);
        setState('not-ready');
      }
    }
  }, [jobID]);

  useEffect(() => { load(); }, [load]);

  function filterAttempts(q, bf) {
    const search  = (q !== undefined ? q : searchQ).toLowerCase();
    const bFilter = bf !== undefined ? bf : breachFilter;
    let filtered  = allAttempts;
    if (search) {
      filtered = filtered.filter(a =>
        (a.prompt   || '').toLowerCase().includes(search) ||
        (a.response || '').toLowerCase().includes(search) ||
        (a.target   || '').toLowerCase().includes(search) ||
        (a.verdict  || '').toLowerCase().includes(search)
      );
    }
    if (bFilter !== '') {
      filtered = filtered.filter(a => String(!!a.breachDetected) === bFilter);
    }
    setFilteredAttempts(filtered);
  }

  if (state === 'loading') return <div className="loader-full"><div className="spinner" /><span>Loading report…</span></div>;

  if (state === 'not-ready') return (
    <div className="report-not-ready">
      <div style={{ fontSize: '48px', opacity: 0.3, marginBottom: '12px' }}>📊</div>
      <h3>Report Not Ready Yet</h3>
      <p className="text-muted text-small mt-2">The attack is still running. Switch to Live Stream to monitor progress.</p>
      <button onClick={load} className="btn btn-outline mt-3">↻ Check Again</button>
    </div>
  );

  const judging  = report?.judging_report || {};
  const summary  = judging.summary || {};
  const perCat   = judging.per_category || [];
  const insights = judging.insights || [];
  const extra    = report?.extra_observations;

  const highSev   = summary.highest_severity || 'NONE';
  const pct       = severityPct(highSev);
  const riskClass = severityClass(highSev);

  // Chart: Breach by Category
  const catLabels   = perCat.map(c => c.category);
  const catBreached = perCat.map(c => c.breached ? 1 : 0);

  // Chart: Verdict distribution
  const verdictCounts = {};
  allAttempts.forEach(a => {
    const v = a.verdict || 'UNKNOWN';
    verdictCounts[v] = (verdictCounts[v] || 0) + 1;
  });
  const vLabels = Object.keys(verdictCounts);
  const vCols   = { SUCCESS:'#00ff88', COMPLIANT:'#00ff88', AMBIGUOUS:'#ffb300', REFUSAL:'#ff4444', FAILED:'#ff4444', PARTIAL:'#00bcd4' };

  return (
    <div>
      {/* Summary stats */}
      <div className="report-summary-grid">
        <div className="report-stat">
          <div className="val">{summary.total_categories || report?.total_categories_processed || 0}</div>
          <div className="lbl">Categories Tested</div>
        </div>
        <div className="report-stat">
          <div className="val" style={{ color: 'var(--accent-red)' }}>{summary.breached || report?.number_of_breaches || 0}</div>
          <div className="lbl">Breaches Detected</div>
        </div>
        <div className="report-stat">
          <div className="val">{highSev}</div>
          <div className="lbl">Highest Severity</div>
        </div>
      </div>

      {/* Risk meter */}
      <div className="card mb-3">
        <div className="card-header">
          <span className="card-title">Overall Risk Level</span>
          <span>{severityBadge(highSev)}</span>
        </div>
        <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
          Avg severity: <strong style={{ color: 'var(--text-primary)' }}>{summary.avg_severity || 'NONE'}</strong>
        </div>
        <div className="risk-bar">
          <div className={`risk-fill ${riskClass}`} style={{ width: `${pct}%` }} />
        </div>
      </div>

      {/* Charts row */}
      <div className="chart-row">
        <div className="card">
          <div className="card-header"><span className="card-title">Breach by Category</span></div>
          <div className="chart-container" style={{ height: '200px' }}>
            {catLabels.length > 0 && (
              <Bar
                data={{
                  labels: catLabels,
                  datasets: [{
                    label: 'Breached',
                    data: catBreached,
                    backgroundColor: perCat.map(c => c.breached ? '#ff444460' : '#00ff8840'),
                    borderColor:     perCat.map(c => c.breached ? '#ff4444' : '#00ff88'),
                    borderWidth: 1, borderRadius: 4,
                  }]
                }}
                options={{
                  responsive: true, maintainAspectRatio: false,
                  scales: { y: { beginAtZero: true, max: 1, ticks: { stepSize: 1, callback: v => v ? 'YES' : 'NO' } } },
                  plugins: { legend: { display: false } }
                }}
              />
            )}
          </div>
        </div>
        <div className="card">
          <div className="card-header"><span className="card-title">Verdict Distribution</span></div>
          <div className="chart-container" style={{ height: '200px' }}>
            {vLabels.length > 0 && (
              <Doughnut
                data={{
                  labels: vLabels,
                  datasets: [{
                    data: vLabels.map(v => verdictCounts[v]),
                    backgroundColor: vLabels.map(v => (vCols[v] || '#8c9db5') + '50'),
                    borderColor:     vLabels.map(v => vCols[v] || '#8c9db5'),
                    borderWidth: 2,
                  }]
                }}
                options={{
                  responsive: true, maintainAspectRatio: false,
                  plugins: { legend: { position: 'right', labels: { padding: 12, font: { size: 11 } } } },
                  cutout: '55%'
                }}
              />
            )}
          </div>
        </div>
      </div>

      {/* Per-category */}
      <div className="card mb-3">
        <div className="card-header"><span className="card-title">Per-Category Analysis</span></div>
        <div className="per-category">
          {perCat.length > 0 ? perCat.map((c, i) => (
            <div key={i} className="cat-row">
              <div className="cat-row-header">
                <span className="cat-name">{c.category || '—'}</span>
                <div className="flex gap-10">
                  {severityBadge(c.severity)}
                  <span className={c.breached ? 'breach-yes' : 'breach-no'}>
                    {c.breached ? '⚠ BREACHED' : '✓ SAFE'}
                  </span>
                </div>
              </div>
              <div className="cat-reasoning">{c.reasoning || ''}</div>
            </div>
          )) : <p className="text-muted text-small">No per-category data.</p>}
        </div>
      </div>

      {/* Judge Insights */}
      <div className="card mb-3">
        <div className="card-header"><span className="card-title">AI Judge Insights</span></div>
        <ul className="insight-list">
          {insights.length > 0
            ? insights.map((ins, i) => <li key={i} className="insight-item">{ins}</li>)
            : <li className="insight-item text-muted">No insights available.</li>
          }
        </ul>
      </div>

      {/* Extra Observations */}
      {extra && Object.keys(extra).length > 0 && (
        <div className="card">
          <div className="card-header"><span className="card-title">Extra Observations</span></div>
          <pre style={{ fontFamily: 'var(--font-code)', fontSize: '12px', color: '#c8d3ea', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
            {JSON.stringify(extra, null, 2)}
          </pre>
        </div>
      )}

      {/* Attempts section (inside report tab, same data) */}
      <div style={{ marginTop: '28px' }}>
        <div className="card-header" style={{ marginBottom: '14px' }}>
          <span className="card-title" style={{ fontSize: '14px' }}>Attempts</span>
          {allAttempts.length > 0 && (
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                className="form-control"
                style={{ width: '200px', padding: '6px 10px', fontSize: '13px' }}
                placeholder="Search…"
                value={searchQ}
                onChange={e => { setSearchQ(e.target.value); filterAttempts(e.target.value, undefined); }}
              />
              <select
                className="form-control"
                style={{ width: '150px', padding: '6px 10px', fontSize: '13px' }}
                value={breachFilter}
                onChange={e => { setBreachFilter(e.target.value); filterAttempts(undefined, e.target.value); }}
              >
                <option value="">All Verdicts</option>
                <option value="true">Breached</option>
                <option value="false">Not Breached</option>
              </select>
            </div>
          )}
        </div>
        {allAttempts.length === 0 ? (
          <div className="empty-state">
            <div className="icon">🎯</div>
            <h3>No attempts recorded yet</h3>
            <p>Attempts are recorded after the attack completes.</p>
          </div>
        ) : (
          <div>
            <div className="text-small text-muted mb-2">{filteredAttempts.length} attempt(s)</div>
            {filteredAttempts.map((a, i) => {
              const breached = a.breachDetected;
              const verdict  = a.verdict || 'UNKNOWN';
              const way      = a.way || a.category || `#${i+1}`;
              const target   = a.target || a.currentCategory || '';
              const field    = a.field ? ` · ${a.field}` : '';
              const round    = a.round != null ? ` · Round ${a.round}` : '';
              const turn     = a.turn_index != null ? ` · Turn ${a.turn_index}` : '';

              return (
                <div key={i} className="attempt-card">
                  <div className="attempt-header">
                    <span className="badge badge-gray">{way}</span>
                    {target && <span className="text-small mono">{target}{field}</span>}
                    <span className="text-small text-muted">{round}{turn}</span>
                    <span
                      className={`badge ${breached ? 'badge-red breach-yes' : 'badge-green breach-no'}`}
                      style={{ marginLeft: 'auto' }}
                    >
                      {breached ? '⚠ BREACHED' : '✓ SAFE'}
                    </span>
                    <span className="badge badge-gray">{verdict}</span>
                  </div>
                  {a.pii_value && (
                    <div className="text-small mb-2">
                      <strong style={{ color: 'var(--accent-red)' }}>PII Found:</strong>{' '}
                      <span className="mono">{a.pii_value}</span>
                    </div>
                  )}
                  {a.evidence && (
                    <div className="text-small mb-2 text-muted">Evidence: {a.evidence}</div>
                  )}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                    <div>
                      <div className="text-small text-muted mb-2">Prompt</div>
                      <div className="prompt-box">{escHtml(a.prompt || a.variationPrompt || '—')}</div>
                    </div>
                    <div>
                      <div className="text-small text-muted mb-2">Response</div>
                      <div className="response-box">{escHtml(a.response || a.response_snippet || a.variationResult || '—')}</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function LiveStreamTab({ jobID }) {
  const [streamStatus, setStreamStatus] = useState('Not connected');
  const [streamRunning, setStreamRunning] = useState(false);
  const [logCount, setLogCount] = useState(0);
  const [autoScroll, setAutoScroll] = useState(true);
  const [logs, setLogs] = useState([]);  // array of { type, data } objects
  const termRef = useRef(null);
  const evtRef  = useRef(null);

  function startStream() {
    if (evtRef.current) evtRef.current.close();
    setLogCount(0);
    setLogs([]);
    setStreamStatus('Connecting…');
    setStreamRunning(true);

    const es = new EventSource(`${API_BASE}/stream/${jobID}`);
    evtRef.current = es;

    es.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === 'connected') {
        setStreamStatus('Connected — streaming logs');
      }
      if (msg.type === 'log') {
        setLogCount(c => c + 1);
        setLogs(prev => [...prev, { kind: 'log', data: msg.data }]);
      }
      if (msg.type === 'report_ready') {
        setLogs(prev => [...prev, { kind: 'raw', text: '✓ Report ready — switch to Vulnerability Report tab.', color: 'var(--accent-green)' }]);
      }
      if (msg.type === 'finished') {
        setStreamStatus('Stream finished');
        setStreamRunning(false);
        es.close(); evtRef.current = null;
        setLogs(prev => [...prev, { kind: 'raw', text: '■ Stream ended.', color: 'var(--text-dim)' }]);
      }
      if (msg.type === 'error') {
        setLogs(prev => [...prev, { kind: 'raw', text: '✗ ' + msg.message, color: 'var(--accent-red)' }]);
      }
    };

    es.onerror = () => {
      setStreamStatus('Connection lost');
      setStreamRunning(false);
    };
  }

  function stopStream() {
    if (evtRef.current) { evtRef.current.close(); evtRef.current = null; }
    setStreamStatus('Stopped');
    setStreamRunning(false);
  }

  function clearTerminal() {
    setLogs([]);
    setLogCount(0);
  }

  useEffect(() => {
    if (autoScroll && termRef.current) {
      termRef.current.scrollTop = termRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  useEffect(() => () => { if (evtRef.current) evtRef.current.close(); }, []);

  const dotClass = `stream-dot${!streamRunning ? ' stopped' : ''}`;

  return (
    <div>
      <div className="stream-status">
        <div className={dotClass} />
        <span>{streamStatus}</span>
        <span className="text-dim" style={{ marginLeft: 'auto' }}>{logCount > 0 ? `${logCount} events` : ''}</span>
      </div>
      <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
        <button onClick={startStream} className="btn btn-sm btn-primary" disabled={streamRunning}>▶ Connect Stream</button>
        <button onClick={stopStream}  className="btn btn-sm btn-outline" disabled={!streamRunning}>■ Stop</button>
        <button onClick={clearTerminal} className="btn btn-sm btn-outline">✕ Clear</button>
        <label className="flex gap-10 text-small text-muted" style={{ cursor: 'pointer' }}>
          <input type="checkbox" checked={autoScroll} onChange={e => setAutoScroll(e.target.checked)} /> Auto-scroll
        </label>
      </div>
      <div className="terminal" ref={termRef}>
        {logs.map((l, i) => {
          if (l.kind === 'raw') {
            return (
              <div key={i} style={{ color: l.color, fontFamily: 'var(--font-code)', fontSize: '12px', padding: '1px 0' }}>
                {l.text}
              </div>
            );
          }
          const d = l.data;
          return (
            <div key={i} className={`log-line log-${d.log_level || 'INFO'}`}>
              <span className="log-time">{(d.timestamp || '').substring(11, 23)}</span>
              <span className="log-type">[{d.message_type || '?'}]</span>
              <span className="log-msg">{escHtml(d.message_text || '')}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function LogsTab({ jobID }) {
  const toast = useToast();
  const [logs, setLogs]     = useState([]);
  const [page, setPage]     = useState(1);
  const [pages, setPages]   = useState(1);
  const [total, setTotal]   = useState(0);
  const [loading, setLoading] = useState(true);

  async function loadLogs(p) {
    setLoading(true);
    try {
      const data = await api(`/jobs/${jobID}/logs?page=${p}&limit=50`);
      setLogs(data.logs);
      setPage(data.page);
      setPages(data.pages);
      setTotal(data.total);
    } catch (e) {
      toast.error('Logs error: ' + e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadLogs(1); }, [jobID]);

  return (
    <div>
      {loading && <div className="loader-full"><div className="spinner" /><span>Loading logs…</span></div>}
      {!loading && (
        <>
          <div className="node-timeline">
            {logs.length === 0 ? (
              <p className="text-muted text-small">No logs recorded yet.</p>
            ) : logs.map((l, i) => (
              <div key={i} className={`node-event ${l.log_level || 'INFO'}`}>
                <span className="ne-time">{fmtDate(l.timestamp)}</span>
                <span className="ne-type">{l.message_type || ''}</span>
                <span className="ne-msg">{escHtml(l.message_text || '')}</span>
                {l.verdict && <span className="badge badge-gray" style={{ flexShrink: 0 }}>{l.verdict}</span>}
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginTop: '14px' }}>
            <button className="btn btn-sm btn-outline" disabled={page <= 1} onClick={() => loadLogs(page - 1)}>← Prev</button>
            <span className="text-small text-muted">Page {page} / {pages} · {total} total</span>
            <button className="btn btn-sm btn-outline" disabled={page >= pages} onClick={() => loadLogs(page + 1)}>Next →</button>
          </div>
        </>
      )}
    </div>
  );
}

function TransactionsTab({ jobID }) {
  const toast = useToast();
  const [txs, setTxs]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    api(`/jobs/${jobID}/transactions`)
      .then(data => { setTxs(data); setLoading(false); })
      .catch(e => { toast.error('TX error: ' + e.message); setLoading(false); });
  }, [jobID]);

  function toggle(id) {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  }

  return (
    <div>
      {loading && <div className="loader-full"><div className="spinner" /><span>Loading transactions…</span></div>}
      {!loading && (
        <div className="node-timeline">
          {txs.length === 0 ? (
            <p className="text-muted text-small">No transaction data yet.</p>
          ) : txs.map((tx, i) => (
            <div key={i}>
              <div className="node-event INFO">
                <span className="ne-time">{fmtDate(tx.timestamp)}</span>
                <span className="ne-type">{escHtml(tx.node_name || '')}</span>
                <span className="ne-msg">
                  Variations: {tx.variation_count || 0} · Breaches: {tx.inc_variation_count || 0}
                  {tx.breach_detected && <span style={{ color: 'var(--accent-red)' }}> · ⚠ BREACH</span>}
                </span>
                <button onClick={() => toggle(tx._id)} className="btn btn-sm btn-outline">Details</button>
              </div>
              {expanded[tx._id] && (
                <div style={{ padding: '10px', background: 'var(--bg-base)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', margin: '-6px 0 6px', fontFamily: 'var(--font-code)', fontSize: '11px', color: '#c8d3ea', whiteSpace: 'pre-wrap', wordBreak: 'break-word', maxHeight: '300px', overflowY: 'auto' }}>
                  {JSON.stringify(tx.state_after || {}, null, 2)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Main JobPage ──────────────────────────────────────────────
export default function JobPage() {
  const { id: jobID } = useParams();
  const toast = useToast();
  const navigate = useNavigate();

  const [job, setJob]       = useState(null);
  const [activeTab, setActiveTab] = useState('report');

  async function loadJobMeta() {
    try {
      const j = await api(`/jobs/${jobID}`);
      setJob(j);
    } catch (e) {
      toast.error('Could not load job: ' + e.message);
    }
  }

  useEffect(() => {
    if (!jobID) { navigate('/dashboard'); return; }
    loadJobMeta();
  }, [jobID]);

  const tabs = [
    { key: 'report',       label: '📊 Vulnerability Report' },
    { key: 'stream',       label: '⚡ Live Stream' },
    { key: 'logs',         label: '📋 Execution Logs' },
    { key: 'transactions', label: '🔄 Transactions' },
  ];

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <header className="topbar">
          <div className="flex gap-10">
            <Link to="/dashboard" className="btn btn-sm btn-outline">Back</Link>
            <div className="topbar-title">{job?.job_name || 'Job Detail'}</div>
          </div>
          <div className="topbar-actions">
            {job && statusBadge(job.job_status)}
            <ThemeToggle />
            <button onClick={loadJobMeta} className="btn btn-outline btn-sm">Refresh</button>
          </div>
        </header>

        <main className="page-body">

          {/* Job meta bar */}
          <div className="job-header">
            <div className="job-meta">
              {job ? (
                <>
                  {jobTypeBadge(job.job_type)}
                  <div className="meta-item">🌐 <span className="mono">{job.targetURL || '—'}</span></div>
                  <div className="meta-item">📅 {fmtDate(job.created_date)}</div>
                  <div className="meta-item">
                    ⚠ Breaches:{' '}
                    <strong style={{ color: job.breachedCount > 0 ? 'var(--accent-red)' : 'var(--accent-green)' }}>
                      {job.breachedCount || 0}
                    </strong>
                  </div>
                  <div className="meta-item">📊 Categories: {job.totalExecutedCategories || 0}</div>
                </>
              ) : <div className="spinner" />}
            </div>
          </div>

          {/* Tabs */}
          <div className="tabs">
            {tabs.map(t => (
              <button
                key={t.key}
                className={`tab-btn${activeTab === t.key ? ' active' : ''}`}
                onClick={() => setActiveTab(t.key)}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Tab Panes */}
          <div className={`tab-pane${activeTab === 'report' ? ' active' : ''}`} id="tab-report">
            {activeTab === 'report' && <ReportTab jobID={jobID} />}
          </div>
          <div className={`tab-pane${activeTab === 'stream' ? ' active' : ''}`} id="tab-stream">
            {activeTab === 'stream' && <LiveStreamTab jobID={jobID} />}
          </div>
          <div className={`tab-pane${activeTab === 'logs' ? ' active' : ''}`} id="tab-logs">
            {activeTab === 'logs' && <LogsTab jobID={jobID} />}
          </div>
          <div className={`tab-pane${activeTab === 'transactions' ? ' active' : ''}`} id="tab-transactions">
            {activeTab === 'transactions' && <TransactionsTab jobID={jobID} />}
          </div>

        </main>
      </div>
    </div>
  );
}
