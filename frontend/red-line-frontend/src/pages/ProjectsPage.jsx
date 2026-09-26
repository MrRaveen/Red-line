import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import ThemeToggle from '../components/ThemeToggle';
import { api, fmtRelative } from '../api';
import { jobTypeBadge, statusBadge } from '../badges.jsx';
import { useToast } from '../ToastContext';

export default function ProjectsPage() {
  const toast = useToast();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  async function loadProjects() {
    try {
      const data = await api('/projects');
      setProjects(data || []);
    } catch (e) {
      toast.error('Could not load projects: ' + e.message);
    } finally {
      setLoading(false);
    }
  }

  async function deleteJob(jobId) {
    if (!window.confirm('Are you sure you want to delete this job and all its data? This action cannot be undone.')) return;
    try {
      await api(`/jobs/${jobId}`, { method: 'DELETE' });
      toast.success('Job deleted successfully');
      loadProjects();
    } catch (err) {
      toast.error('Failed to delete job: ' + err.message);
    }
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <header className="topbar">
          <div className="topbar-title">Projects</div>
          <div className="topbar-actions">
            <ThemeToggle />
            <Link to="/new-job" className="btn btn-primary btn-sm">New Project / Attack</Link>
          </div>
        </header>

        <main className="page-body">
          <div className="card mb-4">
            <div className="card-header">
              <div>
                <span className="card-title">Projects Overview</span>
                <p className="text-muted text-small" style={{ textTransform: 'none', letterSpacing: 0, marginTop: '6px' }}>
                  Projects are grouped automatically by the target LLM URL you test.
                </p>
              </div>
            </div>

            {loading && (
              <div className="loader-full">
                <div className="spinner" />
                <span>Loading projects...</span>
              </div>
            )}

            {!loading && projects.length === 0 && (
              <div className="empty-state">
                <div className="icon">📁</div>
                <h3>No projects yet</h3>
                <p>Launch an attack to automatically create a project for that target.</p>
                <Link to="/new-job" className="btn btn-primary mt-3">＋ Launch Attack</Link>
              </div>
            )}

            {!loading && projects.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {projects.map((p, idx) => (
                  <div
                    key={idx}
                    className="card"
                    style={{ borderLeft: '3px solid var(--accent-blue)', padding: '16px' }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '16px', marginBottom: '4px' }}>
                          {p.project_name || 'Unknown Target'}
                        </div>
                        <div className="text-small text-muted">Last attack: {fmtRelative(p.last_attack)}</div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div className="text-small text-muted mb-1">Total Attacks Executed</div>
                        <div style={{ fontSize: '20px', fontWeight: 700, fontFamily: 'var(--font-code)', color: 'var(--text-primary)' }}>
                          {p.total_jobs}
                        </div>
                      </div>
                    </div>

                    <div className="table-wrap">
                      <table style={{ background: 'var(--bg-base)', borderRadius: 'var(--radius)', overflow: 'hidden' }}>
                        <thead>
                          <tr>
                            <th>Job Name</th>
                            <th>Type</th>
                            <th>Status</th>
                            <th>Breaches</th>
                            <th></th>
                          </tr>
                        </thead>
                        <tbody>
                          {p.jobs.map(j => (
                            <tr key={j.job_id}>
                              <td className="mono">{j.job_name || '—'}</td>
                              <td>{jobTypeBadge(j.job_type)}</td>
                              <td>{statusBadge(j.status)}</td>
                              <td className={`${j.breaches > 0 ? 'severity-HIGH' : 'text-muted'} mono`}>
                                {j.breaches || 0}
                              </td>
                              <td style={{ textAlign: 'right' }}>
                                <Link to={`/job/${j.job_id}`} className="btn btn-sm btn-outline">View Report →</Link>
                                <button
                                  onClick={() => deleteJob(j.job_id)}
                                  className="btn btn-sm btn-outline"
                                  style={{ borderColor: 'var(--accent-red)', color: 'var(--accent-red)', marginLeft: '5px' }}
                                >
                                  Delete
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
