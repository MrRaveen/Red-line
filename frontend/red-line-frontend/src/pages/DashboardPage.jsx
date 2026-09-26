import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Chart as ChartJS,
  ArcElement, BarElement,
  CategoryScale, LinearScale,
  Tooltip, Legend,
} from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import Sidebar from '../components/Sidebar';
import ThemeToggle from '../components/ThemeToggle';
import { api, fmtRelative, typeColor } from '../api';
import { jobTypeBadge, statusBadge } from '../badges.jsx';
import { useToast } from '../ToastContext';

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);
ChartJS.defaults.color = '#8c9db5';
ChartJS.defaults.borderColor = '#1e2d4a';
ChartJS.defaults.font.family = "'Inter', sans-serif";

export default function DashboardPage() {
  const toast    = useToast();
  const navigate = useNavigate();

  const [stats, setStats]         = useState(null);
  const [allJobs, setAllJobs]     = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [lastRefresh, setLastRefresh] = useState('');
  const [searchQ, setSearchQ]     = useState('');

  async function loadDashboard() {
    try {
      const [statsData, jobs] = await Promise.all([
        api('/stats'),
        api('/jobs'),
      ]);
      setStats(statsData);
      setAllJobs(jobs);
      setFilteredJobs(jobs);
      setLastRefresh('Updated ' + new Date().toLocaleTimeString());
    } catch (err) {
      toast.error('Failed to load dashboard: ' + err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
    const interval = setInterval(loadDashboard, 30000);
    return () => clearInterval(interval);
  }, []);

  function filterJobs(q) {
    setSearchQ(q);
    if (!q.trim()) { setFilteredJobs(allJobs); return; }
    const lq = q.toLowerCase();
    setFilteredJobs(allJobs.filter(j =>
      (j.job_name  || '').toLowerCase().includes(lq) ||
      (j.job_type  || '').toLowerCase().includes(lq) ||
      (j.targetURL || '').toLowerCase().includes(lq)
    ));
  }

  async function deleteJob(jobId) {
    if (!window.confirm('Are you sure you want to delete this job and all its data? This action cannot be undone.')) return;
    try {
      await api(`/jobs/${jobId}`, { method: 'DELETE' });
      toast.success('Job deleted successfully');
      loadDashboard();
    } catch (err) {
      toast.error('Failed to delete job: ' + err.message);
    }
  }

  // Chart data
  const typeLabels  = stats?.attack_type_distribution?.map(t => t.type)  ?? [];
  const typeCounts  = stats?.attack_type_distribution?.map(t => t.count) ?? [];
  const typeColors  = typeLabels.map(typeColor);

  const tDates  = stats?.jobs_over_time?.map(d => d.date)  ?? [];
  const tCounts = stats?.jobs_over_time?.map(d => d.count) ?? [];

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <header className="topbar">
          <div className="topbar-title">Dashboard</div>
          <div className="topbar-actions">
            <span className="text-small text-muted">{lastRefresh}</span>
            <ThemeToggle />
            <Link to="/new-job" className="btn btn-primary btn-sm">New Attack</Link>
          </div>
        </header>

        <main className="page-body">

          {/* Stats */}
          <div className="stats-grid">
            <div className="stat-card info">
              <div className="stat-value">{stats?.total_jobs ?? '—'}</div>
              <div className="stat-label">Total Jobs</div>
              <div className="stat-icon">📋</div>
            </div>
            <div className="stat-card warn">
              <div className="stat-value">{stats?.running_jobs ?? '—'}</div>
              <div className="stat-label">Running</div>
              <div className="stat-icon">⚡</div>
            </div>
            <div className="stat-card success">
              <div className="stat-value">{stats?.finished_jobs ?? '—'}</div>
              <div className="stat-label">Finished</div>
              <div className="stat-icon">✓</div>
            </div>
            <div className="stat-card danger">
              <div className="stat-value">{stats?.total_breaches ?? '—'}</div>
              <div className="stat-label">Breaches Found</div>
              <div className="stat-icon">⚠</div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="charts-grid">
            <div className="card">
              <div className="card-header">
                <span className="card-title">Attack Type Distribution</span>
              </div>
              <div className="chart-container">
                {typeLabels.length > 0 && (
                  <Doughnut
                    data={{
                      labels: typeLabels,
                      datasets: [{ data: typeCounts, backgroundColor: typeColors, borderWidth: 2, borderColor: '#111928' }]
                    }}
                    options={{
                      responsive: true, maintainAspectRatio: false,
                      plugins: { legend: { position: 'right', labels: { padding: 14, font: { size: 12 } } } },
                      cutout: '62%'
                    }}
                  />
                )}
              </div>
            </div>
            <div className="card">
              <div className="card-header">
                <span className="card-title">Jobs Over Time</span>
              </div>
              <div className="chart-container">
                {tDates.length > 0 && (
                  <Bar
                    data={{
                      labels: tDates,
                      datasets: [{
                        label: 'Jobs',
                        data: tCounts,
                        backgroundColor: 'rgba(0,255,136,0.3)',
                        borderColor: '#00ff88',
                        borderWidth: 1, borderRadius: 4,
                      }]
                    }}
                    options={{
                      responsive: true, maintainAspectRatio: false,
                      scales: {
                        x: { grid: { display: false } },
                        y: { beginAtZero: true, ticks: { stepSize: 1 } }
                      },
                      plugins: { legend: { display: false } }
                    }}
                  />
                )}
              </div>
            </div>
          </div>

          {/* Jobs Table */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Recent Jobs</span>
              <input
                type="text"
                className="form-control"
                style={{ width: '220px', padding: '6px 10px', fontSize: '13px' }}
                placeholder="Search jobs…"
                value={searchQ}
                onChange={e => filterJobs(e.target.value)}
              />
            </div>

            {loading && (
              <div className="loader-full">
                <div className="spinner" />
                <span>Loading jobs…</span>
              </div>
            )}

            {!loading && filteredJobs.length === 0 && (
              <div className="empty-state">
                <div className="icon">📋</div>
                <h3>No jobs yet</h3>
                <p>Start your first attack test to see results here.</p>
                <Link to="/new-job" className="btn btn-primary mt-3">＋ New Attack</Link>
              </div>
            )}

            {!loading && filteredJobs.length > 0 && (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Job Name</th>
                      <th>Attack Type</th>
                      <th>Target URL</th>
                      <th>Status</th>
                      <th>Breaches</th>
                      <th>Created</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredJobs.map(j => (
                      <tr key={j._id}>
                        <td>
                          <Link to={`/job/${j._id}`} className="mono">{j.job_name || '—'}</Link>
                        </td>
                        <td>{jobTypeBadge(j.job_type)}</td>
                        <td className="truncate text-muted mono text-small">{j.targetURL || '—'}</td>
                        <td>{statusBadge(j.job_status)}</td>
                        <td className={`${j.breachedCount > 0 ? 'severity-HIGH' : 'text-muted'} mono`}>
                          {j.breachedCount || 0}
                        </td>
                        <td className="text-muted text-small">{fmtRelative(j.created_date)}</td>
                        <td>
                          <Link to={`/job/${j._id}`} className="btn btn-sm btn-outline">View →</Link>
                          <button
                            onClick={() => deleteJob(j._id)}
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
            )}
          </div>

        </main>
      </div>
    </div>
  );
}
