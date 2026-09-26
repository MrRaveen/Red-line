import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ToastProvider } from './ToastContext';
import { Auth } from './api';
import LoginPage    from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import NewJobPage   from './pages/NewJobPage';
import JobPage      from './pages/JobPage';
import ProjectsPage from './pages/ProjectsPage';

function ProtectedRoute({ children }) {
  if (!Auth.isLoggedIn()) return <Navigate to="/" replace />;
  return children;
}

function AuthRoute({ children }) {
  if (Auth.isLoggedIn()) return <Navigate to="/dashboard" replace />;
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <Routes>
          <Route path="/" element={
            <AuthRoute><LoginPage /></AuthRoute>
          } />
          <Route path="/dashboard" element={
            <ProtectedRoute><DashboardPage /></ProtectedRoute>
          } />
          <Route path="/new-job" element={
            <ProtectedRoute><NewJobPage /></ProtectedRoute>
          } />
          <Route path="/job/:id" element={
            <ProtectedRoute><JobPage /></ProtectedRoute>
          } />
          <Route path="/projects" element={
            <ProtectedRoute><ProjectsPage /></ProtectedRoute>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </ToastProvider>
    </BrowserRouter>
  );
}
