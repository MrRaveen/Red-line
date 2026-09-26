import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, Auth } from '../api';

export default function LoginPage() {
  const navigate = useNavigate();
  const [tab, setTab] = useState('login'); // 'login' | 'register'

  // Login state
  const [lUsername, setLUsername] = useState('');
  const [lPassword, setLPassword] = useState('');
  const [loginErr, setLoginErr] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  // Register state
  const [rUsername, setRUsername] = useState('');
  const [rEmail, setREmail] = useState('');
  const [rPassword, setRPassword] = useState('');
  const [regErr, setRegErr] = useState('');
  const [regOk, setRegOk] = useState('');
  const [regLoading, setRegLoading] = useState(false);

  async function doLogin(e) {
    e.preventDefault();
    setLoginLoading(true);
    setLoginErr('');
    try {
      const data = await api('/auth/login', {
        method: 'POST',
        body: { username: lUsername.trim(), password: lPassword },
      });
      Auth.set(data.userID, data.email || '');
      navigate('/dashboard');
    } catch (ex) {
      setLoginErr(ex.message);
    } finally {
      setLoginLoading(false);
    }
  }

  async function doRegister(e) {
    e.preventDefault();
    setRegLoading(true);
    setRegErr('');
    setRegOk('');
    try {
      await api('/auth/register', {
        method: 'POST',
        body: { username: rUsername.trim(), email: rEmail.trim(), password: rPassword },
      });
      setRegOk('Account created! You can now sign in.');
      setTimeout(() => setTab('login'), 1500);
    } catch (ex) {
      setRegErr(ex.message);
    } finally {
      setRegLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-box">
        <div className="auth-logo">
          <div className="logo-big">RL</div>
          <h1>Red-Line</h1>
          <p>LLM Security Testing Platform</p>
        </div>

        <div className="auth-toggle">
          <button
            className={tab === 'login' ? 'active' : ''}
            onClick={() => setTab('login')}
          >
            Sign In
          </button>
          <button
            className={tab === 'register' ? 'active' : ''}
            onClick={() => setTab('register')}
          >
            Register
          </button>
        </div>

        {/* Login Form */}
        {tab === 'login' && (
          <form onSubmit={doLogin}>
            <div className="form-group">
              <label className="form-label">Username</label>
              <input
                type="text"
                className="form-control"
                placeholder="your username"
                value={lUsername}
                onChange={e => setLUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                placeholder="••••••••"
                value={lPassword}
                onChange={e => setLPassword(e.target.value)}
                required
              />
            </div>
            {loginErr && (
              <div className="alert alert-error">{loginErr}</div>
            )}
            <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%' }} disabled={loginLoading}>
              {loginLoading ? <><span className="spinner" /> Signing in…</> : 'Sign In'}
            </button>
          </form>
        )}

        {/* Register Form */}
        {tab === 'register' && (
          <form onSubmit={doRegister}>
            <div className="form-group">
              <label className="form-label">Username</label>
              <input
                type="text"
                className="form-control"
                placeholder="choose a username"
                value={rUsername}
                onChange={e => setRUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                type="email"
                className="form-control"
                placeholder="analyst@company.com"
                value={rEmail}
                onChange={e => setREmail(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                placeholder="••••••••"
                value={rPassword}
                onChange={e => setRPassword(e.target.value)}
                required
              />
            </div>
            {regErr && <div className="alert alert-error">{regErr}</div>}
            {regOk  && <div className="alert alert-success">{regOk}</div>}
            <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%' }} disabled={regLoading}>
              {regLoading ? <><span className="spinner" /> Creating…</> : 'Create Account'}
            </button>
          </form>
        )}

        <p className="text-muted text-small mt-3" style={{ textAlign: 'center' }}>
          Red-Line v1.0
        </p>
      </div>
    </div>
  );
}
