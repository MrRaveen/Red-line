import { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Auth } from '../api';

export default function Sidebar({ activePage }) {
  const navigate = useNavigate();
  const userID = Auth.userID;

  function logout() {
    Auth.clear();
    navigate('/');
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">RL</div>
        <div>
          <div className="logo-text">Red-Line</div>
          <div className="logo-sub">SECURITY PLATFORM</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Overview</div>
        <NavLink
          to="/dashboard"
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
        >
          Dashboard
        </NavLink>

        <div className="nav-section-label">Testing</div>
        <NavLink
          to="/new-job"
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
        >
          New Attack
        </NavLink>
        <NavLink
          to="/projects"
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
        >
          Projects
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <div className="user-badge">
          <div className="user-avatar">{userID ? userID[0].toUpperCase() : '?'}</div>
          <span className="text-small">{userID}</span>
        </div>
        <button onClick={logout} className="btn btn-sm btn-outline" style={{ padding: '4px 8px', fontSize: '11px' }}>
          Sign out
        </button>
      </div>
    </aside>
  );
}
