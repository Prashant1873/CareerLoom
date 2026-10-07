import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Building2,
  Search,
  X,
  ExternalLink,
  RefreshCw,
  AlertCircle,
  Sparkles,
} from 'lucide-react';
import type { BatchSyncStatus, CareerTarget, CareerTargetStats } from '../types/job';
import {
  fetchTargets,
  fetchTargetStats,
  fetchSyncStatus,
  triggerBatchSync,
} from '../services/api';
import './CareerDirectoryModal.css';

interface CareerDirectoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectCompany?: (companyName: string) => void;
}

export const CareerDirectoryModal: React.FC<CareerDirectoryModalProps> = ({
  isOpen,
  onClose,
  onSelectCompany,
}) => {
  const [targets, setTargets] = useState<CareerTarget[]>([]);
  const [stats, setStats] = useState<CareerTargetStats | null>(null);
  const [syncStatus, setSyncStatus] = useState<BatchSyncStatus | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedTier, setSelectedTier] = useState<string>('all');
  const [selectedDomain, setSelectedDomain] = useState<string>('all');
  const [isSyncTriggering, setIsSyncTriggering] = useState<boolean>(false);
  const [syncNotice, setSyncNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Load target list and stats
  const loadDirectoryData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [targetData, statsData, statusData] = await Promise.all([
        fetchTargets({
          tier: selectedTier !== 'all' ? selectedTier : undefined,
          domain: selectedDomain !== 'all' ? selectedDomain : undefined,
          search: searchQuery.trim() || undefined,
          limit: 100,
        }),
        fetchTargetStats(),
        fetchSyncStatus(),
      ]);

      setTargets(targetData.items);
      setStats(statsData);
      setSyncStatus(statusData);
    } catch (err) {
      console.error('Failed to load career targets:', err);
      setError('Failed to load career targets from local database. Check backend connection or refresh the page.');
    } finally {
      setIsLoading(false);
    }
  }, [selectedTier, selectedDomain, searchQuery]);

  useEffect(() => {
    if (isOpen) {
      loadDirectoryData();
    }
  }, [isOpen, loadDirectoryData]);

  // Handle escape key to close modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedTier('all');
    setSelectedDomain('all');
  };

  const handleTriggerSync = async () => {
    setIsSyncTriggering(true);
    setSyncNotice(null);
    try {
      const result = await triggerBatchSync();
      setSyncNotice(result.message || 'Batch synchronization initiated in background');
      // Refresh sync status
      const statusData = await fetchSyncStatus();
      setSyncStatus(statusData);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Batch synchronization in progress or failed to start';
      setSyncNotice(msg);
    } finally {
      setIsSyncTriggering(false);
    }
  };

  const formattedJobCount = useMemo(() => {
    if (!stats || !stats.total_live_jobs) return '16,000+';
    return stats.total_live_jobs.toLocaleString();
  }, [stats]);

  if (!isOpen) return null;

  return (
    <div
      className="directory-modal-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="directory-modal-title"
    >
      <div className="directory-modal-container">
        {/* Modal Top Header */}
        <div className="directory-modal-header">
          <div className="directory-brand-wrap">
            <div className="directory-brand-icon">
              <Building2 size={20} />
            </div>
            <div className="directory-title-area">
              <div className="directory-title-row">
                <h2 id="directory-modal-title" className="directory-modal-title">
                  Career Directory Hub
                </h2>
                <span className="directory-count-badge">
                  {stats?.total_targets || targets.length} Employers
                </span>
              </div>
              <p className="directory-subtitle">
                Verified Global & Indian Direct Career Portals
              </p>
            </div>
          </div>

          {/* Search Box */}
          <div className="directory-search-box">
            <Search size={15} className="directory-search-icon" />
            <input
              type="text"
              className="directory-search-input"
              placeholder="Search 230+ companies by name, domain, or ATS..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label="Search employers in directory"
            />
            {searchQuery && (
              <button
                type="button"
                className="directory-search-clear"
                onClick={() => setSearchQuery('')}
                title="Clear search query"
                aria-label="Clear search query"
              >
                <X size={13} />
              </button>
            )}
          </div>

          {/* Modal Close Button */}
          <button
            type="button"
            className="directory-close-btn"
            onClick={onClose}
            aria-label="Close directory modal"
            title="Close directory modal (Esc)"
          >
            <X size={18} />
          </button>
        </div>

        {/* Stats & Sync Toolbar */}
        <div className="directory-stats-toolbar">
          <div className="directory-metrics-group">
            <div className="directory-metric-item">
              <span className="metric-label">Monitored Employers:</span>
              <span className="metric-value">{stats?.total_targets || 237}</span>
            </div>
            <div className="directory-metric-item">
              <span className="metric-label">Verified Live Feeds:</span>
              <span className="metric-value">{stats?.active_targets || 237}</span>
            </div>
            <div className="directory-metric-item">
              <span className="metric-label">Indexed Openings:</span>
              <span className="metric-value">{formattedJobCount}</span>
            </div>
          </div>

          <button
            type="button"
            className="directory-sync-btn"
            onClick={handleTriggerSync}
            disabled={syncStatus?.is_running || isSyncTriggering}
            aria-label="Trigger Background Sync"
          >
            <RefreshCw
              size={13}
              className={syncStatus?.is_running || isSyncTriggering ? 'spin-icon' : ''}
            />
            <span>
              {syncStatus?.is_running
                ? 'Syncing In Progress...'
                : isSyncTriggering
                ? 'Triggering...'
                : 'Trigger Background Sync'}
            </span>
          </button>
        </div>

        {syncNotice && (
          <div className="directory-stats-toolbar" style={{ backgroundColor: 'var(--bg-subtle)' }}>
            <span style={{ fontSize: '12px', color: 'var(--accent-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Sparkles size={13} /> {syncNotice}
            </span>
          </div>
        )}

        {/* Filter Controls Bar */}
        <div className="directory-filters-bar">
          <div className="tier-pills-row" role="tablist" aria-label="Employer Category Tiers">
            {[
              { id: 'all', label: 'All Employers' },
              { id: 'unicorn', label: '🦄 Unicorns' },
              { id: 'startup', label: '🚀 Startups' },
              { id: 'enterprise', label: '🏢 Conglomerates' },
              { id: 'consulting', label: '💼 Consulting' },
            ].map((tier) => (
              <button
                key={tier.id}
                type="button"
                className={`tier-pill-btn ${selectedTier === tier.id ? 'active' : ''}`}
                onClick={() => setSelectedTier(tier.id)}
                role="tab"
                aria-selected={selectedTier === tier.id}
              >
                {tier.label}
              </button>
            ))}
          </div>

          <div className="domain-select-wrap">
            <select
              className="domain-select-input"
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              aria-label="Filter directory by industry domain"
            >
              <option value="all">All Domains</option>
              <option value="Tech">Tech / Software</option>
              <option value="Fintech">Fintech</option>
              <option value="Quantitative Finance">Quantitative Finance</option>
              <option value="Consulting">Strategy & Consulting</option>
              <option value="Healthcare">Healthcare & Biotech</option>
            </select>
          </div>
        </div>

        {/* Main Scrollable Content */}
        <div className="directory-scroll-content">
          {error && (
            <div className="directory-error-banner" role="alert">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertCircle size={16} />
                <span>{error}</span>
              </div>
              <button
                type="button"
                className="retry-connect-btn"
                onClick={loadDirectoryData}
              >
                Retry Connection
              </button>
            </div>
          )}

          {isLoading ? (
            <div className="directory-cards-grid">
              {Array.from({ length: 8 }).map((_, idx) => (
                <div key={idx} className="directory-card-skeleton">
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <div className="skeleton-shimmer" style={{ width: '40px', height: '40px' }} />
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <div className="skeleton-shimmer" style={{ width: '60%', height: '16px' }} />
                      <div className="skeleton-shimmer" style={{ width: '40%', height: '12px' }} />
                    </div>
                  </div>
                  <div className="skeleton-shimmer" style={{ width: '100%', height: '24px' }} />
                  <div className="skeleton-shimmer" style={{ width: '100%', height: '32px' }} />
                </div>
              ))}
            </div>
          ) : targets.length === 0 ? (
            <div className="directory-empty-card">
              <Building2 size={40} className="text-zinc-500" />
              <h3 className="empty-title">
                No Employers Found Matching Filter Criteria
              </h3>
              <p className="empty-description">
                Adjust your search terms, clear active role tier filters, or switch to All Employers to view the complete catalog.
              </p>
              <button
                type="button"
                className="reset-directory-btn"
                onClick={handleResetFilters}
              >
                Reset Directory Filters
              </button>
            </div>
          ) : (
            <div className="directory-cards-grid">
              {targets.map((target) => {
                const initial = (target.name || 'C').charAt(0).toUpperCase();
                const tierClass = `tier-${(target.category_tier || 'startup').toLowerCase()}`;
                const atsClass = `ats-${(target.ats_type || 'custom').toLowerCase()}`;

                return (
                  <div key={target.id} className="directory-card">
                    <div className="card-top-row">
                      <div className="company-monogram" aria-hidden="true">
                        {initial}
                      </div>
                      <div className="card-title-group">
                        <span className="company-name" title={target.name}>
                          {target.name}
                        </span>
                        <div className="card-badges-row">
                          <span className={`tier-tag ${tierClass}`}>
                            {target.category_tier || 'Startup'}
                          </span>
                          <span className="domain-tag">
                            {target.domain || 'Tech'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="card-meta-row">
                      <span className={`ats-pill ${atsClass}`}>
                        {target.ats_type?.toUpperCase() || 'DIRECT ATS'}
                      </span>
                      <span className="live-count-pill">
                        {target.job_count > 0 ? (
                          <>
                            <span className="pulse-dot" style={{ width: '6px', height: '6px' }} />
                            <span>{target.job_count} open roles</span>
                          </>
                        ) : (
                          <span style={{ color: 'var(--text-muted)' }}>Feed Active</span>
                        )}
                      </span>
                    </div>

                    <div className="card-actions-row">
                      <a
                        href={target.career_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="portal-cta-btn"
                        title={`Open official career portal for ${target.name}`}
                        aria-label={`Launch career portal for ${target.name}`}
                      >
                        <ExternalLink size={13} />
                        <span>Launch Career Portal</span>
                      </a>
                      {onSelectCompany && (
                        <button
                          type="button"
                          className="explore-stream-btn"
                          onClick={() => {
                            onSelectCompany(target.name);
                            onClose();
                          }}
                          title={`Filter main stream for ${target.name} openings`}
                          aria-label={`Explore jobs for ${target.name}`}
                        >
                          Explore
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
