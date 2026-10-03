import React from 'react';
import {
  Search,
  Sparkles,
  X,
  ArrowUpDown,
  Building2,
  MapPin,
  Calendar,
  Zap,
  Bookmark,
  ExternalLink,
  MessageSquare,
  AlertCircle,
  Command,
} from 'lucide-react';
import type { FilterState, JobItem, ParsedQuery } from '../types/job';
import { formatJobDate } from '../utils/dateFormatter';

interface MasterJobStreamProps {
  jobs: JobItem[];
  totalCount?: number;
  selectedJob: JobItem | null;
  onSelectJob: (job: JobItem) => void;
  isLoading: boolean;
  isBookmarked: (id: string) => boolean;
  onToggleBookmark: (id: string) => void;
  onOpenInsights: (job: JobItem) => void;
  query: string;
  onQueryChange: (q: string) => void;
  onSearch: (q: string) => void;
  parsedQuery: ParsedQuery | null;
  filters: FilterState;
  onFilterChange: (partial: Partial<FilterState>) => void;
  onResetFilters: () => void;
  searchRef?: React.RefObject<HTMLInputElement | null>;
}

export const MasterJobStream: React.FC<MasterJobStreamProps> = ({
  jobs,
  totalCount,
  selectedJob,
  onSelectJob,
  isLoading,
  isBookmarked,
  onToggleBookmark,
  onOpenInsights,
  query,
  onQueryChange,
  onSearch,
  parsedQuery,
  filters,
  onFilterChange,
  onResetFilters,
  searchRef,
}) => {
  const activeChips: { label: string; onClear: () => void }[] = [];

  if (filters.searchPrompt) {
    activeChips.push({
      label: `"${filters.searchPrompt}"`,
      onClear: () => onFilterChange({ searchPrompt: '' }),
    });
  }
  if (filters.category) {
    activeChips.push({
      label: filters.category.replace(/_/g, ' '),
      onClear: () => onFilterChange({ category: '' }),
    });
  }
  if (filters.isRemote === true) {
    activeChips.push({
      label: 'Remote',
      onClear: () => onFilterChange({ isRemote: null }),
    });
  } else if (filters.isRemote === false) {
    activeChips.push({
      label: 'Onsite',
      onClear: () => onFilterChange({ isRemote: null }),
    });
  }
  if (filters.seniority) {
    activeChips.push({
      label: filters.seniority,
      onClear: () => onFilterChange({ seniority: '' }),
    });
  }
  if (filters.country) {
    activeChips.push({
      label: filters.country,
      onClear: () => onFilterChange({ country: '' }),
    });
  }
  if (filters.domain) {
    activeChips.push({
      label: filters.domain,
      onClear: () => onFilterChange({ domain: '' }),
    });
  }
  if (filters.freshnessDays) {
    activeChips.push({
      label: `< ${filters.freshnessDays === 1 ? '24 Hours' : `${filters.freshnessDays} Days`}`,
      onClear: () => onFilterChange({ freshnessDays: null }),
    });
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch(query);
    }
  };

  return (
    <div className="master-stream-container">
      {/* Sticky Omnibox Search Header */}
      <div className="stream-search-header">
        <div className="omnibox-wrapper">
          <Search size={16} className="omnibox-icon" />
          <input
            ref={searchRef}
            type="text"
            className="omnibox-input"
            placeholder="Search roles in natural language... (e.g., 'entry level product in Europe or remote')"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            onKeyDown={handleKeyDown}
            aria-label="Search jobs"
          />
          {query ? (
            <button
              type="button"
              className="omnibox-clear"
              onClick={() => onQueryChange('')}
              title="Clear search"
            >
              <X size={14} />
            </button>
          ) : (
            <div className="omnibox-key-hint">
              <span className="key-badge">/</span>
            </div>
          )}
        </div>

        {/* NLP Parsing Indicator */}
        {parsedQuery && (
          <div className="nlp-insight-pill">
            <Sparkles size={12} className="text-emerald-400" />
            <span className="nlp-pill-text">
              Parsed via {parsedQuery.model_provider || 'AI'}:
              {parsedQuery.category && ` Category: ${parsedQuery.category}`}
              {parsedQuery.country && ` • Region: ${parsedQuery.country}`}
              {parsedQuery.is_remote !== null && ` • ${parsedQuery.is_remote ? 'Remote' : 'Onsite'}`}
            </span>
          </div>
        )}

        {/* Active Filter Chips */}
        {activeChips.length > 0 && (
          <div className="active-chips-row">
            <span className="chips-label">Active:</span>
            {activeChips.map((chip, idx) => (
              <span key={idx} className="filter-chip">
                <span>{chip.label}</span>
                <button
                  type="button"
                  className="chip-remove-btn"
                  onClick={chip.onClear}
                  aria-label={`Remove filter ${chip.label}`}
                >
                  <X size={11} />
                </button>
              </span>
            ))}
            <button type="button" className="clear-all-chips-btn" onClick={onResetFilters}>
              Clear all
            </button>
          </div>
        )}

        {/* Stream Toolbar & Controls */}
        <div className="stream-toolbar">
          <div className="stream-count-info">
            <span className="count-number">
              {(totalCount !== undefined ? totalCount : jobs.length).toLocaleString()}
            </span>
            <span className="count-label">
              {filters.savedOnly
                ? 'saved opportunities'
                : totalCount && totalCount > jobs.length
                ? `verified openings (showing first ${jobs.length})`
                : 'verified openings'}
            </span>
          </div>

          <div className="stream-toolbar-right">
            <div className="sort-control">
              <ArrowUpDown size={12} className="sort-icon" />
              <select
                className="sort-select"
                value={filters.sortBy}
                onChange={(e) => onFilterChange({ sortBy: e.target.value as 'date' | 'company' | 'title' })}
                aria-label="Sort jobs"
              >
                <option value="date">Newest Posted</option>
                <option value="company">Company (A-Z)</option>
                <option value="title">Role Title</option>
              </select>
            </div>

            <div className="keyboard-nav-hint hide-mobile" title="Keyboard shortcuts: J (next), K (prev), S (save), Enter (apply)">
              <Command size={11} />
              <span>J / K to navigate</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stream Job Cards List */}
      <div className="stream-cards-list" role="feed" aria-label="Job opportunities list">
        {isLoading ? (
          <div className="stream-skeletons">
            {Array.from({ length: 7 }).map((_, idx) => (
              <div key={idx} className="stream-card-skeleton skeleton" />
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="stream-empty-state">
            <AlertCircle size={36} className="text-zinc-500 mb-3" />
            <h3 className="empty-title">
              {filters.savedOnly ? 'No saved jobs' : 'No matching positions'}
            </h3>
            <p className="empty-desc">
              {filters.savedOnly
                ? 'Press S on any job card or click the bookmark button to save it.'
                : 'Try adjusting your search prompt or resetting filters.'}
            </p>
            <button type="button" className="stream-reset-btn" onClick={onResetFilters}>
              Reset all filters
            </button>
          </div>
        ) : (
          jobs.map((job) => {
            const isSelected = selectedJob?.id === job.id;
            const { relative, exact, tier } = formatJobDate(job.date_posted);
            const saved = isBookmarked(job.id);

            return (
              <div
                key={job.id}
                className={`stream-job-card ${isSelected ? 'selected' : ''}`}
                onClick={() => onSelectJob(job)}
                role="article"
                tabIndex={0}
                aria-selected={isSelected}
              >
                {/* Selected Accent Bar */}
                {isSelected && <div className="selected-indicator-bar" />}

                {/* Card Top Row */}
                <div className="card-header-line">
                  <div className="company-info-group">
                    <div className="stream-company-logo">
                      <Building2 size={14} />
                    </div>
                    <div>
                      <span className="stream-company-name">{job.company}</span>
                      {job.domain && <span className="stream-domain-tag">{job.domain}</span>}
                    </div>
                  </div>

                  {/* Dual Date Badge */}
                  <div className={`stream-date-badge tier-${tier}`} title={`Posted on ${exact}`}>
                    <Calendar size={11} />
                    <span className="relative-text">{relative}</span>
                  </div>
                </div>

                {/* Role Title */}
                <h4 className="stream-job-title" title={job.title}>
                  {job.title}
                </h4>

                {/* Attributes Row */}
                <div className="stream-attrs-row">
                  <div className="stream-attr-location">
                    <MapPin size={12} />
                    <span>{job.location || 'Multiple Locations'}</span>
                  </div>

                  {job.is_remote && (
                    <span className="stream-remote-tag">
                      <Zap size={10} /> Remote
                    </span>
                  )}

                  {job.seniority && (
                    <span className="stream-seniority-tag">
                      {job.seniority.charAt(0).toUpperCase() + job.seniority.slice(1)}
                    </span>
                  )}
                </div>

                {/* Card Footer Quick Actions */}
                <div className="stream-card-footer">
                  <div className="footer-left-buttons">
                    <button
                      type="button"
                      className={`stream-bookmark-btn ${saved ? 'bookmarked' : ''}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        onToggleBookmark(job.id);
                      }}
                      title={saved ? 'Remove bookmark (S)' : 'Save job (S)'}
                    >
                      <Bookmark size={13} fill={saved ? 'currentColor' : 'none'} />
                    </button>

                    <button
                      type="button"
                      className="stream-intel-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onOpenInsights(job);
                      }}
                      title="View interview process & Reddit discussions"
                    >
                      <MessageSquare size={12} className="text-orange-400" />
                      <span>Intel</span>
                    </button>
                  </div>

                  <button
                    type="button"
                    className="stream-apply-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(job.apply_url, '_blank', 'noopener,noreferrer');
                    }}
                    title="Apply directly on company portal"
                  >
                    <span>Apply</span>
                    <ExternalLink size={12} />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
