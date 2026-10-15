import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import './ThemeToggle.css';

interface ThemeToggleProps {
  collapsed?: boolean;
  className?: string;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ collapsed = false, className = '' }) => {
  const { toggleTheme, setTheme, isDark } = useTheme();

  if (collapsed) {
    return (
      <button
        type="button"
        onClick={toggleTheme}
        className={`theme-toggle-collapsed ${className}`}
        aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
        title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      >
        {isDark ? <Sun size={16} className="theme-icon sun-icon" /> : <Moon size={16} className="theme-icon moon-icon" />}
      </button>
    );
  }

  return (
    <div className={`theme-toggle-segmented ${className}`} role="radiogroup" aria-label="Theme selection">
      <button
        type="button"
        role="radio"
        aria-checked={isDark}
        onClick={() => setTheme('dark')}
        className={`theme-segment-btn ${isDark ? 'active' : ''}`}
      >
        <Moon size={13} className="segment-icon" />
        <span>Dark</span>
      </button>
      <button
        type="button"
        role="radio"
        aria-checked={!isDark}
        onClick={() => setTheme('light')}
        className={`theme-segment-btn ${!isDark ? 'active' : ''}`}
      >
        <Sun size={13} className="segment-icon" />
        <span>Light</span>
      </button>
    </div>
  );
};
