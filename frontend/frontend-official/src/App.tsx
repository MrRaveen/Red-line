import { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  if (!isLoggedIn) {
    return <Login onLogin={() => setIsLoggedIn(true)} />;
  }

  return <Dashboard onLogout={() => setIsLoggedIn(false)} />;
}

function Login({ onLogin }: { onLogin: () => void }) {
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // fake login
    onLogin();
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Welcome Back</h2>
        <p>Please enter your credentials to access the dashboard.</p>
        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label>Username</label>
            <input type="text" required placeholder="admin" />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input type="password" required placeholder="••••••••" />
          </div>
          <button type="submit" className="primary-btn">Login</button>
        </form>
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
    const url = 'http://127.0.0.1:5000/api/v1/stream';
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
