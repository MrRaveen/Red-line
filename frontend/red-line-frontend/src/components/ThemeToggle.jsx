import { useState, useEffect } from 'react';

export default function ThemeToggle() {
  const [theme, setTheme] = useState(() => localStorage.getItem('rl_theme') || 'dark');

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('rl_theme', theme);
  }, [theme]);

  return (
    <button
      className="btn btn-sm btn-outline"
      onClick={() => setTheme(t => t === 'light' ? 'dark' : 'light')}
    >
      {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
    </button>
  );
}
