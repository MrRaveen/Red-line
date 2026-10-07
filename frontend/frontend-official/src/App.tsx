import { useState, useEffect, useRef } from 'react';
import './App.css';

import { authService } from './services/authService';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(authService.isAuthenticated());

  if (!isLoggedIn) {
    return <Auth onLogin={() => setIsLoggedIn(true)} />;
  }

  const handleLogout = () => {
    authService.logout();
    setIsLoggedIn(false);
  };

  return <Dashboard onLogout={handleLogout} />;
}

function Auth({ onLogin }: { onLogin: () => void }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      if (isLogin) {
        const res = await authService.login(email, password);
        if (res.ok) {
          onLogin();
        } else {
          setError(res.data.message || 'Login failed');
        }
      } else {
        const res = await authService.register(username, email, password);
        if (res.status === 'success') {
          // auto login after register or just switch to login tab
          setIsLogin(true);
          setError('Account created! Please login.');
        } else {
          setError(res.message || 'Registration failed');
        }
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
        <p>{isLogin ? 'Please enter your credentials to access the dashboard.' : 'Sign up to get started.'}</p>
        
        {error && <div style={{ color: error.includes('created') ? 'green' : 'red', marginBottom: '1rem' }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="input-group">
              <label>Username</label>
              <input type="text" required value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" />
            </div>
          )}
          <div className="input-group">
            <label>Email</label>
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="email@example.com" />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" />
          </div>
          <button type="submit" className="primary-btn">{isLogin ? 'Login' : 'Register'}</button>
        </form>
        
        <p style={{ marginTop: '1rem', cursor: 'pointer', color: '#007bff' }} onClick={() => { setIsLogin(!isLogin); setError(''); }}>
          {isLogin ? "Don't have an account? Register" : "Already have an account? Login"}
        </p>
      </div>
    </div>
  );
}

function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [activeTab, setActiveTab] = useState<'home' | 'realtime'>('home');

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <div className="logo">Red-Line</div>
        <nav>
          <button 
            className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
          >
            Home
          </button>
          <button 
            className={`nav-item ${activeTab === 'realtime' ? 'active' : ''}`}
            onClick={() => setActiveTab('realtime')}
          >
            Realtime Logs
          </button>
        </nav>
        <button className="logout-btn" onClick={onLogout}>Logout</button>
      </aside>
      <main className="main-content">
        {activeTab === 'home' ? <HomeTab /> : <RealtimeTab />}
      </main>
    </div>
  );
}

function HomeTab() {
  return (
    <div className="tab-content">
      <h2>Dashboard Home</h2>
      <p>Welcome to your Red-Line dashboard. Use the sidebar to navigate to different sections.</p>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Events</h3>
          <p className="stat-value">1,204</p>
        </div>
        <div className="stat-card">
          <h3>Active Streams</h3>
          <p className="stat-value">3</p>
        </div>
        <div className="stat-card">
          <h3>System Health</h3>
          <p className="stat-value success">Optimal</p>
        </div>
      </div>
    </div>
  );
}

function RealtimeTab() {
  const [logs, setLogs] = useState<string[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const startStream = () => {
    if (isStreaming) return;
    
    // Connect to the Flask SSE endpoint
    const url = 'http://127.0.0.1:8001/api/v1/stream';
    const sse = new EventSource(url);
    
    sse.onmessage = (e) => {
      // Ignore keepalives (they are typically sent as comments or empty data, but just in case)
      if (e.data === ':keepalive') return;
      
      const timestamp = new Date().toLocaleTimeString();
      let logData = e.data;
      
      // Try to format JSON nicely if it is JSON
      try {
        const parsed = JSON.parse(e.data);
        logData = JSON.stringify(parsed, null, 2);
      } catch (err) {
        // Not JSON, leave as is
      }
      
      setLogs((prev) => [...prev, `[${timestamp}] ${logData}`]);
    };

    sse.onerror = () => {
      setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] Connection error. Reconnecting...`]);
    };

    eventSourceRef.current = sse;
    setIsStreaming(true);
    setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] Stream connected.`]);
  };

  const stopStream = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsStreaming(false);
    setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] Stream disconnected by user.`]);
  };

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom of logs
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="tab-content h-full">
      <div className="realtime-header">
        <h2>Realtime Log Dispenser</h2>
        <div className="controls">
          {!isStreaming ? (
            <button className="primary-btn" onClick={startStream}>Connect Stream</button>
          ) : (
            <button className="danger-btn" onClick={stopStream}>Disconnect Stream</button>
          )}
          <button className="secondary-btn" onClick={() => setLogs([])}>Clear Logs</button>
        </div>
      </div>
      
      <div className="log-viewer">
        {logs.length === 0 ? (
          <div className="empty-logs">No logs to display yet. Click Connect to start receiving events.</div>
        ) : (
          logs.map((log, i) => (
            <pre key={i} className="log-entry" style={{ margin: 0, fontFamily: 'inherit' }}>
              {log}
            </pre>
          ))
        )}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
}

export default App;
