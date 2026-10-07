import React, { useState } from 'react';
import {
  Compass,
  Bookmark,
  Zap,
  Calendar,
  Layers,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  RotateCcw,
  Sparkles,
  Globe,
  Briefcase,
  Code2,
  Cpu,
  LineChart,
  UserCheck,
  Stethoscope,
  Building,
  Building2,
} from 'lucide-react';
import type { Category, FilterState } from '../types/job';

interface NavRailProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  categories: Category[];
  selectedCategory: string;
  onSelectCategory: (id: string) => void;
  totalJobsCount: number;
  savedCount: number;
  showSavedOnly: boolean;
  onToggleSavedOnly: () => void;
  freshnessDays: number | null;
  onSelectFreshness: (days: number | null) => void;
  filters: FilterState;
  onFilterChange: (partial: Partial<FilterState>) => void;
  onResetFilters: () => void;
  onOpenDirectory?: () => void;
  monitoredCount?: number;
  syncFreshnessText?: string;
  isSyncing?: boolean;
}

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  software_engineering: <Code2 size={15} />,
  data_ai: <Cpu size={15} />,
  product_management: <Compass size={15} />,
  quantitative_finance: <LineChart size={15} />,
  management_consulting: <Briefcase size={15} />,
  design_ux: <Sparkles size={15} />,
  cybersecurity: <UserCheck size={15} />,
  healthcare_biotech: <Stethoscope size={15} />,
};

export const NavRail: React.FC<NavRailProps> = ({
  isCollapsed,
  onToggleCollapse,
  categories,
  selectedCategory,
  onSelectCategory,
  totalJobsCount,
  savedCount,
  showSavedOnly,
  onToggleSavedOnly,
  freshnessDays,
  onSelectFreshness,
  filters,
  onFilterChange,
  onResetFilters,
  onOpenDirectory,
  monitoredCount,
  syncFreshnessText,
  isSyncing,
}) => {
  const [isCategoriesOpen, setIsCategoriesOpen] = useState(true);
  const [isFiltersOpen, setIsFiltersOpen] = useState(true);

  const hasActiveFilters = Boolean(
    filters.searchPrompt ||
      filters.category ||
      filters.domain ||
      filters.country ||
      filters.isRemote !== null ||
      filters.seniority ||
      filters.freshnessDays !== null ||
      showSavedOnly
  );

  return (
    <aside className={`nav-rail ${isCollapsed ? 'collapsed' : 'expanded'}`}>
      {/* Rail Top Brand */}
      <div className="rail-header">
        <div className="rail-brand" onClick={() => onResetFilters()} role="button" tabIndex={0}>
          <div className="brand-logo-gem">
            <Sparkles size={16} className="text-emerald-400" />
          </div>
          {!isCollapsed && (
            <div className="brand-title-wrap">
              <span className="brand-title">CareerLoom</span>
              <span className="brand-version-pill">v2.0</span>
            </div>
          )}
        </div>

        <button
          type="button"
          className="rail-collapse-toggle"
          onClick={onToggleCollapse}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Rail Scroll Content */}
      <div className="rail-scroll-body">
        {/* Quick Views */}
        <div className="rail-section">
          {!isCollapsed && <span className="rail-section-label">Views</span>}

          <div className="rail-nav-items">
            {/* Career Directory Hub Navigation Trigger */}
            {onOpenDirectory && (
              <button
                type="button"
                className="rail-nav-btn career-directory-nav-btn"
                onClick={onOpenDirectory}
                title="Explore monitored employer career portals and ATS feeds"
              >
                <div className="nav-btn-left">
                  <Building2 size={16} className="nav-icon text-cyan-400" />
                  {!isCollapsed && <span className="nav-text font-medium">Career Directory</span>}
                </div>
                {!isCollapsed && (
                  <span className="nav-count-badge directory-count-pill">{monitoredCount || 230}+</span>
                )}
              </button>
            )}

            <button
              type="button"
              className={`rail-nav-btn ${!showSavedOnly && !freshnessDays && filters.country !== 'India' && !filters.category ? 'active' : ''}`}
              onClick={() => {
                if (showSavedOnly) onToggleSavedOnly();
                onSelectFreshness(null);
                onFilterChange({ country: '', category: '', metroHub: undefined });
              }}
              title="All verified opportunities"
            >
              <div className="nav-btn-left">
                <Compass size={16} className="nav-icon" />
                {!isCollapsed && <span className="nav-text">All Listings</span>}
              </div>
              {!isCollapsed && (
                <span className="nav-count-badge">{totalJobsCount}</span>
              )}
            </button>

            {/* India Direct Quick View */}
            <button
              type="button"
              className={`rail-nav-btn india-direct-nav-btn ${filters.country === 'India' && filters.category !== 'product_cluster' && filters.category !== 'strategy_cluster' ? 'active' : ''}`}
              onClick={() => {
                if (showSavedOnly) onToggleSavedOnly();
                if (filters.country === 'India' && !filters.category) {
                  onFilterChange({ country: '', metroHub: undefined });
                } else {
                  onFilterChange({ country: 'India', category: '', metroHub: undefined });
                }
              }}
              title="Filter exclusively for verified jobs across Indian Unicorns & Tech Hubs"
            >
              <div className="nav-btn-left">
                <span className="india-flag-icon" role="img" aria-label="India flag">🇮🇳</span>
                {!isCollapsed && <span className="nav-text font-medium">India Direct</span>}
              </div>
              {!isCollapsed && (
                <span className="nav-count-badge india-badge">1.4k</span>
              )}
            </button>

            {/* 1-Click Product Management Quick Filter (V5-UI-02) */}
            <button
              type="button"
              className={`rail-nav-btn pm-direct-nav-btn ${filters.category === 'product_cluster' && filters.country === 'India' ? 'active' : ''}`}
              onClick={() => {
                if (showSavedOnly) onToggleSavedOnly();
                if (filters.category === 'product_cluster' && filters.country === 'India') {
                  onFilterChange({ category: '', country: '' });
                } else {
                  onFilterChange({ category: 'product_cluster', country: 'India', metroHub: undefined });
                }
              }}
              title="Filter for verified Product Management openings across India"
            >
              <div className="nav-btn-left">
                <span className="india-flag-icon" role="img" aria-label="India flag">🇮🇳</span>
                {!isCollapsed && <span className="nav-text font-medium">🇮🇳 PM Roles</span>}
              </div>
              {!isCollapsed && (
                <span className="nav-count-badge pm-badge">PM</span>
              )}
            </button>

            {/* 1-Click Strategy & Consulting Quick Filter (V5-UI-02) */}
            <button
              type="button"
              className={`rail-nav-btn strategy-direct-nav-btn ${filters.category === 'strategy_cluster' && filters.country === 'India' ? 'active' : ''}`}
              onClick={() => {
                if (showSavedOnly) onToggleSavedOnly();
                if (filters.category === 'strategy_cluster' && filters.country === 'India') {
                  onFilterChange({ category: '', country: '' });
                } else {
                  onFilterChange({ category: 'strategy_cluster', country: 'India', metroHub: undefined });
                }
              }}
              title="Filter for Strategy, Consulting & Founder's Office openings across India"
            >
              <div className="nav-btn-left">
                <span className="india-flag-icon" role="img" aria-label="India flag">🇮🇳</span>
                {!isCollapsed && <span className="nav-text font-medium">🇮🇳 Strategy</span>}
              </div>
              {!isCollapsed && (
                <span className="nav-count-badge strategy-badge">Strategy</span>
              )}
            </button>

            <button
              type="button"
              className={`rail-nav-btn ${showSavedOnly ? 'active' : ''}`}
              onClick={onToggleSavedOnly}
              title="Saved opportunities"
            >
              <div className="nav-btn-left">
                <Bookmark size={16} className="nav-icon" />
                {!isCollapsed && <span className="nav-text">Saved</span>}
              </div>
              {!isCollapsed && savedCount > 0 && (
                <span className="nav-count-badge saved-badge">{savedCount}</span>
              )}
            </button>

            <button
              type="button"
              className={`rail-nav-btn ${freshnessDays === 1 ? 'active' : ''}`}
              onClick={() => {
                if (showSavedOnly) onToggleSavedOnly();
                onSelectFreshness(freshnessDays === 1 ? null : 1);
              }}
              title="Posted in the last 24 hours"
            >
              <div className="nav-btn-left">
                <Zap size={16} className="nav-icon text-emerald-400" />
                {!isCollapsed && <span className="nav-text">Past 24 Hours</span>}
              </div>
              {!isCollapsed && <span className="fresh-dot" />}
            </button>

            <button
              type="button"
              className={`rail-nav-btn ${freshnessDays === 7 ? 'active' : ''}`}
              onClick={() => {
                if (showSavedOnly) onToggleSavedOnly();
                onSelectFreshness(freshnessDays === 7 ? null : 7);
              }}
              title="Posted in the last 7 days"
            >
              <div className="nav-btn-left">
                <Calendar size={16} className="nav-icon" />
                {!isCollapsed && <span className="nav-text">Past 7 Days</span>}
              </div>
            </button>
          </div>
        </div>

        {/* Categories Section */}
        {!isCollapsed ? (
          <div className="rail-section">
            <div
              className="rail-accordion-header"
              onClick={() => setIsCategoriesOpen(!isCategoriesOpen)}
            >
              <div className="accordion-title-row">
                <Layers size={14} className="text-zinc-400" />
                <span className="rail-section-label">Role Tracks</span>
              </div>
              <ChevronDown
                size={14}
                className={`accordion-chevron ${isCategoriesOpen ? 'open' : ''}`}
              />
            </div>

            {isCategoriesOpen && (
              <div className="rail-categories-list">
                <button
                  type="button"
                  className={`rail-cat-item ${!selectedCategory ? 'active' : ''}`}
                  onClick={() => onSelectCategory('')}
                >
                  <span className="cat-name">Any Category</span>
                </button>

                {categories.map((cat) => {
                  const icon = CATEGORY_ICONS[cat.id] || <Briefcase size={14} />;
                  return (
                    <button
                      key={cat.id}
                      type="button"
                      className={`rail-cat-item ${selectedCategory === cat.id ? 'active' : ''}`}
                      onClick={() => onSelectCategory(cat.id === selectedCategory ? '' : cat.id)}
                      title={cat.description}
                    >
                      <div className="cat-icon-wrap">{icon}</div>
                      <span className="cat-name">{cat.label}</span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        ) : (
          <div className="rail-collapsed-category-icons">
            {categories.slice(0, 6).map((cat) => (
              <button
                key={cat.id}
                type="button"
                className={`rail-collapsed-icon-btn ${selectedCategory === cat.id ? 'active' : ''}`}
                onClick={() => onSelectCategory(cat.id === selectedCategory ? '' : cat.id)}
                title={cat.label}
              >
                {CATEGORY_ICONS[cat.id] || <Briefcase size={16} />}
              </button>
            ))}
          </div>
        )}

        {/* Faceted Filters Accordion */}
        {!isCollapsed && (
          <div className="rail-section">
            <div
              className="rail-accordion-header"
              onClick={() => setIsFiltersOpen(!isFiltersOpen)}
            >
              <div className="accordion-title-row">
                <SlidersHorizontal size={14} className="text-zinc-400" />
                <span className="rail-section-label">Filters</span>
              </div>
              <ChevronDown
                size={14}
                className={`accordion-chevron ${isFiltersOpen ? 'open' : ''}`}
              />
            </div>

            {isFiltersOpen && (
              <div className="rail-filters-content">
                {/* Work Mode */}
                <div className="filter-group-mini">
                  <span className="mini-label">Work Mode</span>
                  <div className="filter-segmented">
                    <button
                      type="button"
                      className={`seg-btn ${filters.isRemote === null ? 'active' : ''}`}
                      onClick={() => onFilterChange({ isRemote: null })}
                    >
                      All
                    </button>
                    <button
                      type="button"
                      className={`seg-btn ${filters.isRemote === true ? 'active' : ''}`}
                      onClick={() => onFilterChange({ isRemote: true })}
                    >
                      Remote
                    </button>
                    <button
                      type="button"
                      className={`seg-btn ${filters.isRemote === false ? 'active' : ''}`}
                      onClick={() => onFilterChange({ isRemote: false })}
                    >
                      Onsite
                    </button>
                  </div>
                </div>

                {/* Seniority */}
                <div className="filter-group-mini">
                  <span className="mini-label">Seniority</span>
                  <div className="filter-chips-grid">
                    {['', 'entry', 'mid', 'senior', 'lead'].map((s) => (
                      <button
                        key={s}
                        type="button"
                        className={`chip-btn ${filters.seniority === s ? 'active' : ''}`}
                        onClick={() => onFilterChange({ seniority: s })}
                      >
                        {s ? s.charAt(0).toUpperCase() + s.slice(1) : 'All'}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Country / Region */}
                <div className="filter-group-mini">
                  <span className="mini-label">Geography</span>
                  <div className="filter-select-wrap">
                    <Globe size={13} className="select-icon" />
                    <select
                      className="filter-select-input"
                      value={filters.country}
                      onChange={(e) => onFilterChange({ country: e.target.value, metroHub: undefined })}
                      aria-label="Filter by Country or Region"
                    >
                      <option value="">Global / All Regions</option>
                      <option value="India">🇮🇳 India</option>
                      <option value="United States">United States</option>
                      <option value="United Kingdom">United Kingdom</option>
                      <option value="Europe">Europe (Regional)</option>
                      <option value="Canada">Canada</option>
                      <option value="Germany">Germany</option>
                      <option value="Singapore">Singapore</option>
                    </select>
                  </div>
                </div>

                {/* Metro Hub Filter (Available when India is active) */}
                {filters.country === 'India' && (
                  <div className="filter-group-mini animate-fade-in">
                    <span className="mini-label">Indian Tech Hub</span>
                    <div className="filter-chips-grid">
                      {[
                        { id: '', label: 'All India' },
                        { id: 'Bengaluru', label: 'BLR' },
                        { id: 'Delhi NCR', label: 'NCR' },
                        { id: 'Hyderabad', label: 'HYD' },
                        { id: 'Pune', label: 'PUN' },
                        { id: 'Mumbai', label: 'BOM' },
                        { id: 'Chennai', label: 'MAA' },
                      ].map((hub) => (
                        <button
                          key={hub.id}
                          type="button"
                          className={`chip-btn ${(filters.metroHub || '') === hub.id ? 'active' : ''}`}
                          onClick={() => onFilterChange({ metroHub: hub.id || undefined })}
                        >
                          {hub.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Industry Domain */}
                <div className="filter-group-mini">
                  <span className="mini-label">Domain</span>
                  <div className="filter-select-wrap">
                    <Building size={13} className="select-icon" />
                    <select
                      className="filter-select-input"
                      value={filters.domain}
                      onChange={(e) => onFilterChange({ domain: e.target.value })}
                      aria-label="Filter by Industry Domain"
                    >
                      <option value="">All Domains</option>
                      <option value="Tech">Tech / Software</option>
                      <option value="Fintech">Fintech</option>
                      <option value="Quantitative Finance">Quantitative Finance</option>
                      <option value="Consulting">Strategy & Consulting</option>
                      <option value="Healthcare">Healthcare & Biotech</option>
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Rail Footer */}
      <div className="rail-footer">
        {hasActiveFilters && !isCollapsed && (
          <button
            type="button"
            className="rail-reset-btn"
            onClick={onResetFilters}
            title="Reset all active filters"
          >
            <RotateCcw size={13} />
            <span>Reset Filters</span>
          </button>
        )}
        {!isCollapsed ? (
          <div
            className="rail-live-indicator"
            onClick={onOpenDirectory}
            role="button"
            tabIndex={0}
            title="Click to view all monitored employer portals and sync health"
            style={{ cursor: onOpenDirectory ? 'pointer' : 'default' }}
          >
            <span className={`status-ping ${isSyncing ? 'status-ping-amber' : ''}`} />
            <span className="status-text">
              {monitoredCount || 230}+ Employers • {syncFreshnessText || 'Active Feeds'}
            </span>
          </div>
        ) : (
          <span
            className={`status-ping-mini ${isSyncing ? 'status-ping-amber' : ''}`}
            title={`${monitoredCount || 230}+ Employers • ${syncFreshnessText || 'Active Feeds'}`}
            onClick={onOpenDirectory}
            style={{ cursor: onOpenDirectory ? 'pointer' : 'default' }}
          />
        )}
      </div>
    </aside>
  );
};
