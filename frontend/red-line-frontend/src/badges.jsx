/**
 * Badge JSX components — port of app.js badge functions
 */

export function JobTypeBadge({ type }) {
  if (!type) return <span className="badge badge-gray">—</span>;
  const map = {
    'prompt injection':        'badge-blue',
    'halusination attack':     'badge-purple',
    'PII exfilteration attack':'badge-yellow',
    'jailbreak attack':        'badge-red',
  };
  const cls = map[type] || 'badge-gray';
  return <span className={`badge ${cls}`}>{type}</span>;
}

export function StatusBadge({ status }) {
  if (status === 'FINISHED') return <span className="badge badge-green">FINISHED</span>;
  return <span className="badge badge-yellow">PROCESSING</span>;
}

export function SeverityBadge({ severity: sev }) {
  const map = { NONE:'badge-gray', LOW:'badge-green', MEDIUM:'badge-yellow', HIGH:'badge-red', CRITICAL:'badge-red' };
  return <span className={`badge ${map[sev] || 'badge-gray'} severity-${sev}`}>{sev || 'NONE'}</span>;
}

// Convenience wrapper functions (for JSX usage in templates)
export function jobTypeBadge(type) { return <JobTypeBadge type={type} />; }
export function statusBadge(status) { return <StatusBadge status={status} />; }
export function severityBadge(sev)  { return <SeverityBadge severity={sev} />; }
