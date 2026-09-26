import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import ThemeToggle from '../components/ThemeToggle';
import { api, Auth } from '../api';
import { useToast } from '../ToastContext';

const TYPE_DESCRIPTIONS = {
  'prompt injection':         'Semantic steering to override system instructions via word-level substitution.',
  'PII exfilteration attack': 'Few-shot + chaining technique to extract emails, phones, and SSNs.',
  'jailbreak attack':         'Multi-turn adversarial conversation to bypass safety guardrails.',
  'halusination attack':      'Probes for hallucinated package names and fabricated information.',
};

export default function NewJobPage() {
  const toast    = useToast();
  const navigate = useNavigate();

  const [attackTypes, setAttackTypes] = useState([]);
  const [name,   setName]   = useState('');
  const [desc,   setDesc]   = useState('');
  const [type,   setType]   = useState('');
  const [url,    setUrl]    = useState('');
  const [err,    setErr]    = useState('');
  const [ok,     setOk]     = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAttackTypes();
  }, []);

  async function loadAttackTypes() {
    try {
      const data = await api('/attack-types');
      setAttackTypes(data.attack_types);
    } catch (e) {
      toast.error('Could not load attack types: ' + e.message);
    }
  }

  async function startAttack(e) {
    e.preventDefault();
    setLoading(true);
    setErr('');
    setOk('');

    const payload = {
      userID:      Auth.userID,
      job_name:    name.trim(),
      description: desc.trim(),
      job_type:    type,
      targetURL:   url.trim(),
    };

    try {
      await api('/jobs/start', { method: 'POST', body: payload });
      setOk('✓ Attack launched! Redirecting to job view…');
      setTimeout(async () => {
        try {
          const jobs = await api('/jobs');
          if (jobs.length) navigate(`/job/${jobs[0]._id}`);
          else navigate('/dashboard');
        } catch { navigate('/dashboard'); }
      }, 2000);
    } catch (ex) {
      setErr(ex.message);
      setLoading(false);
    }
  }

  const typeInfo = type && TYPE_DESCRIPTIONS[type] ? '🔍 ' + TYPE_DESCRIPTIONS[type] : '';

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <header className="topbar">
          <div className="topbar-title">Launch New Attack</div>
          <div className="topbar-actions">
            <ThemeToggle />
            <Link to="/dashboard" className="btn btn-outline btn-sm">← Back</Link>
          </div>
        </header>

        <main className="page-body" style={{ maxWidth: '720px' }}>

          <div className="card">
            <div className="card-header">
              <span className="card-title">Attack Configuration</span>
            </div>

            <form onSubmit={startAttack}>
              <div className="form-group">
                <label className="form-label">
                  Job Name <span style={{ color: 'var(--accent-red)' }}>*</span>
                </label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. PII Extraction Test — Customer Service LLM"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  className="form-control"
                  rows="2"
                  placeholder="Brief description of this test session…"
                  value={desc}
                  onChange={e => setDesc(e.target.value)}
                />
              </div>

              <div className="row">
                <div className="col">
                  <div className="form-group">
                    <label className="form-label">
                      Attack Type <span style={{ color: 'var(--accent-red)' }}>*</span>
                    </label>
                    <select
                      className="form-control"
                      value={type}
                      onChange={e => setType(e.target.value)}
                      required
                    >
                      <option value="">Select attack type…</option>
                      {attackTypes.map(t => (
                        <option key={t} value={t}>{t}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="col">
                  <div className="form-group">
                    <label className="form-label">
                      Target LLM URL <span style={{ color: 'var(--accent-red)' }}>*</span>
                    </label>
                    <input
                      type="url"
                      className="form-control"
                      placeholder="http://host:port/api/generate"
                      value={url}
                      onChange={e => setUrl(e.target.value)}
                      required
                    />
                  </div>
                </div>
              </div>

              {typeInfo && (
                <div className="alert alert-info mb-3">{typeInfo}</div>
              )}

              {err && <div className="alert alert-error">{err}</div>}
              {ok  && <div className="alert alert-success">{ok}</div>}

              <div className="flex gap-10">
                <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
                  {loading ? <><span className="spinner" /> Launching…</> : '⚡ Launch Attack'}
                </button>
                <Link to="/dashboard" className="btn btn-outline btn-lg">Cancel</Link>
              </div>
            </form>
          </div>

          {/* Attack type reference */}
          <div className="card mt-4">
            <div className="card-header">
              <span className="card-title">Attack Type Reference</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '14px' }}>
                <div className="flex gap-10 mb-3">
                  <span className="badge badge-blue">Prompt Injection</span>
                </div>
                <p className="text-small text-muted">Tests if the LLM can be manipulated to ignore system instructions via carefully crafted user inputs using word-level substitution and semantic steering.</p>
              </div>
              <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '14px' }}>
                <div className="flex gap-10 mb-3">
                  <span className="badge badge-yellow">PII Exfiltration</span>
                </div>
                <p className="text-small text-muted">Attempts to extract personally identifiable information (email, phone, SSN) via few-shot learning and prompt chaining techniques.</p>
              </div>
              <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '14px' }}>
                <div className="flex gap-10 mb-3">
                  <span className="badge badge-red">Jailbreak Attack</span>
                </div>
                <p className="text-small text-muted">Multi-turn attack attempting to bypass LLM safety guardrails by iteratively escalating adversarial prompts across multiple conversation turns.</p>
              </div>
              <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '14px' }}>
                <div className="flex gap-10 mb-3">
                  <span className="badge badge-purple">Hallucination</span>
                </div>
                <p className="text-small text-muted">Detects hallucination vulnerabilities by probing for fabricated package names, fake citations, or non-existent information generation.</p>
              </div>
            </div>
          </div>

        </main>
      </div>
    </div>
  );
}
