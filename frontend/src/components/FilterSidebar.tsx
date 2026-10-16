import React from 'react';
import { Filter, RotateCcw, Clock, Globe, Briefcase, Award, ArrowUpDown, Laptop } from 'lucide-react';
import type { FilterState } from '../types/job';
import { IndiaFlag } from './IndiaFlag';

interface FilterSidebarProps {
  filters: FilterState;
  onFilterChange: (filters: Partial<FilterState>) => void;
  onResetFilters: () => void;
  totalFilteredCount: number;
}

const FRESHNESS_OPTIONS = [
  { label: 'Any Time', value: null },
  { label: 'Past 24 Hours', value: 1 },
  { label: 'Past 7 Days', value: 7 },
  { label: 'Past 14 Days', value: 14 },
  { label: 'Past 30 Days', value: 30 },
];

const DOMAIN_OPTIONS = [
  { label: 'All Domains', value: '' },
  { label: 'Tech & Software', value: 'tech' },
  { label: 'AI & Data Science', value: 'data_ai' },
  { label: 'Quantitative Finance', value: 'finance_quant' },
  { label: 'Strategy Consulting', value: 'consulting' },
];

const REGION_OPTIONS = [
  { label: 'All Locations', value: '' },
  { label: 'United States', value: 'United States' },
  { label: 'United Kingdom', value: 'United Kingdom' },
  { label: 'European Union', value: 'Europe' },
  { label: 'India', value: 'India' },
  { label: 'Singapore', value: 'Singapore' },
  { label: 'Remote / Global', value: 'Remote' },
];

const SENIORITY_OPTIONS = [
  { label: 'All Levels', value: '' },
  { label: 'Entry / Junior / Intern', value: 'entry' },
  { label: 'Mid-Level', value: 'mid' },
  { label: 'Senior', value: 'senior' },
  { label: 'Staff / Lead / Exec', value: 'lead' },
];

export const FilterSidebar: React.FC<FilterSidebarProps> = ({
  filters,
  onFilterChange,
  onResetFilters,
  totalFilteredCount,
}) => {
  const activeCount = [
    filters.category !== '',
    filters.domain !== '',
    filters.country !== '',
    filters.isRemote !== null,
    filters.seniority !== '',
    filters.freshnessDays !== null,
  ].filter(Boolean).length;

  return (
    <aside className="filter-sidebar">
      <div className="sidebar-header">
        <div className="sidebar-title">
          <Filter size={16} />
          <span>Faceted Filters</span>
          {activeCount > 0 && <span className="active-badge">{activeCount}</span>}
        </div>
        <div className="sidebar-count-hint">
          {totalFilteredCount} {totalFilteredCount === 1 ? 'match' : 'matches'}
        </div>
        {activeCount > 0 && (
          <button
            type="button"
            className="reset-filters-btn"
            onClick={onResetFilters}
            title="Reset all filters"
          >
            <RotateCcw size={13} />
            <span>Reset</span>
          </button>
        )}
      </div>

      {/* Freshness Section */}
      <div className="filter-group">
        <div className="filter-group-title">
          <Clock size={14} className="filter-icon" />
          <span>Date Posted</span>
        </div>
        <div className="segmented-control">
          {FRESHNESS_OPTIONS.map((opt) => {
            const isSelected = filters.freshnessDays === opt.value;
            return (
              <button
                key={opt.label}
                type="button"
                className={`segment-btn ${isSelected ? 'active' : ''}`}
                onClick={() => onFilterChange({ freshnessDays: opt.value })}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Work Mode / Remote */}
      <div className="filter-group">
        <div className="filter-group-title">
          <Laptop size={14} className="filter-icon" />
          <span>Work Mode</span>
        </div>
        <div className="pill-group">
          <button
            type="button"
            className={`toggle-pill ${filters.isRemote === null ? 'active' : ''}`}
            onClick={() => onFilterChange({ isRemote: null })}
          >
            Any Mode
          </button>
          <button
            type="button"
            className={`toggle-pill ${filters.isRemote === true ? 'active' : ''}`}
            onClick={() => onFilterChange({ isRemote: true })}
          >
            Remote Only
          </button>
          <button
            type="button"
            className={`toggle-pill ${filters.isRemote === false ? 'active' : ''}`}
            onClick={() => onFilterChange({ isRemote: false })}
          >
            Onsite / Hybrid
          </button>
        </div>
      </div>

      {/* Region / Country */}
      <div className="filter-group">
        <div className="filter-group-title">
          {filters.country === 'India' ? (
            <IndiaFlag size={14} className="filter-icon" />
          ) : (
            <Globe size={14} className="filter-icon" />
          )}
          <span>Region & Country</span>
        </div>
        <select
          className="filter-select"
          value={filters.country}
          onChange={(e) => onFilterChange({ country: e.target.value, metroHub: undefined })}
        >
          {REGION_OPTIONS.map((r) => (
            <option key={r.value} value={r.value}>
              {r.label}
            </option>
          ))}
        </select>
      </div>

      {/* Indian Tech Hub Filter (Visible when India is active) */}
      {filters.country === 'India' && (
        <div className="filter-group animate-fade-in">
          <div className="filter-group-title">
            <IndiaFlag size={15} style={{ marginRight: 6 }} />
            <span>Indian Tech Hub</span>
          </div>
          <select
            className="filter-select"
            value={filters.metroHub || ''}
            onChange={(e) => onFilterChange({ metroHub: e.target.value || undefined })}
          >
            <option value="">All India (1,400+ jobs)</option>
            <option value="Bengaluru">Bengaluru / Bangalore (BLR)</option>
            <option value="Delhi NCR">Delhi NCR / Gurgaon / Noida</option>
            <option value="Hyderabad">Hyderabad / Cyberabad (HYD)</option>
            <option value="Pune">Pune (PUN)</option>
            <option value="Mumbai">Mumbai / Navi Mumbai (BOM)</option>
            <option value="Chennai">Chennai (MAA)</option>
            <option value="Remote">Remote (India)</option>
          </select>
        </div>
      )}

      {/* Industry Domain */}
      <div className="filter-group">
        <div className="filter-group-title">
          <Briefcase size={14} className="filter-icon" />
          <span>Industry Domain</span>
        </div>
        <select
          className="filter-select"
          value={filters.domain}
          onChange={(e) => onFilterChange({ domain: e.target.value })}
        >
          {DOMAIN_OPTIONS.map((d) => (
            <option key={d.value} value={d.value}>
              {d.label}
            </option>
          ))}
        </select>
      </div>

      {/* Experience / Seniority */}
      <div className="filter-group">
        <div className="filter-group-title">
          <Award size={14} className="filter-icon" />
          <span>Experience Level</span>
        </div>
        <div className="seniority-grid">
          {SENIORITY_OPTIONS.map((s) => (
            <button
              key={s.value}
              type="button"
              className={`seniority-btn ${filters.seniority === s.value ? 'active' : ''}`}
              onClick={() => onFilterChange({ seniority: s.value })}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Sorting */}
      <div className="filter-group">
        <div className="filter-group-title">
          <ArrowUpDown size={14} className="filter-icon" />
          <span>Sort Listings</span>
        </div>
        <select
          className="filter-select"
          value={filters.sortBy}
          onChange={(e) => onFilterChange({ sortBy: e.target.value as 'date' | 'company' | 'title' })}
        >
          <option value="date">Posting Date (Newest First)</option>
          <option value="company">Company Name (A-Z)</option>
          <option value="title">Job Title (A-Z)</option>
        </select>
      </div>
    </aside>
  );
};
