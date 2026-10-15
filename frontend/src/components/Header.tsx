import React from 'react';
import { Compass, Bookmark } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

interface HeaderProps {
  savedCount: number;
  showSavedOnly: boolean;
  onToggleSavedOnly: () => void;
  totalJobs: number;
}

export const Header: React.FC<HeaderProps> = ({
  savedCount,
  showSavedOnly,
  onToggleSavedOnly,
  totalJobs,
}) => {
  return (
    <header className="site-header">
      <div className="header-container">
        <div className="brand-group">
          <div className="logo-badge">
            <Compass className="logo-icon" size={22} />
          </div>
          <div className="brand-text">
            <div className="brand-title-row">
              <span className="brand-title">CareerLoom</span>
              <span className="live-pill">
                <span className="pulse-dot" /> Live Feeds
              </span>
            </div>
            <p className="brand-tagline">Global ATS Career Portal Discovery Engine</p>
          </div>
        </div>

        <div className="header-stats">
          <div className="stat-pill">
            <span className="stat-label">Indexed Listings:</span>
            <span className="stat-value">{totalJobs > 0 ? totalJobs.toLocaleString() : '1,000+'}</span>
          </div>
          <div className="stat-pill hide-mobile">
            <span className="stat-label">Coverage:</span>
            <span className="stat-value">55+ Top Global Firms</span>
          </div>
          <button
            type="button"
            className={`saved-toggle-btn ${showSavedOnly ? 'active' : ''}`}
            onClick={onToggleSavedOnly}
            title={showSavedOnly ? 'Show all listings' : 'Show bookmarked listings'}
            aria-pressed={showSavedOnly}
          >
            <Bookmark size={16} fill={showSavedOnly ? 'currentColor' : 'none'} />
            <span>Saved Jobs</span>
            <span className="saved-counter">{savedCount}</span>
          </button>
          <ThemeToggle collapsed={true} />
        </div>
      </div>
    </header>
  );
};
