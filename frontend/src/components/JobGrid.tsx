import React from 'react';
import { Briefcase, AlertCircle, ArrowRight } from 'lucide-react';
import type { JobItem } from '../types/job';
import { JobCard } from './JobCard';

interface JobGridProps {
  jobs: JobItem[];
  isLoading: boolean;
  isBookmarked: (id: string) => boolean;
  onToggleBookmark: (id: string) => void;
  onSelectJob: (job: JobItem) => void;
  onResetFilters: () => void;
  hasActiveFilters: boolean;
  isSavedTab: boolean;
}

export const JobGrid: React.FC<JobGridProps> = ({
  jobs,
  isLoading,
  isBookmarked,
  onToggleBookmark,
  onSelectJob,
  onResetFilters,
  hasActiveFilters,
  isSavedTab,
}) => {
  if (isLoading) {
    return (
      <div className="job-grid-section">
        <div className="grid-header-skeleton skeleton" style={{ height: '36px', marginBottom: '16px' }} />
        <div className="job-cards-grid">
          {Array.from({ length: 6 }).map((_, idx) => (
            <div key={idx} className="job-card-skeleton skeleton" />
          ))}
        </div>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="empty-state-card animate-fade-in">
        <div className="empty-state-icon">
          {isSavedTab ? <Briefcase size={36} /> : <AlertCircle size={36} />}
        </div>
        <h3 className="empty-title">
          {isSavedTab ? 'No saved jobs yet' : 'No matching positions found'}
        </h3>
        <p className="empty-desc">
          {isSavedTab
            ? 'Bookmark opportunities by clicking the bookmark icon on any job card to save them for later.'
            : 'Try broadening your search prompt, resetting regional or date filters, or choosing one of the popular discovery tracks.'}
        </p>
        {hasActiveFilters && !isSavedTab && (
          <button
            type="button"
            className="empty-action-btn"
            onClick={onResetFilters}
          >
            <span>Reset All Filters</span>
            <ArrowRight size={14} />
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="job-grid-section">
      <div className="job-cards-grid">
        {jobs.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            isBookmarked={isBookmarked(job.id)}
            onToggleBookmark={onToggleBookmark}
            onSelectJob={onSelectJob}
          />
        ))}
      </div>
    </div>
  );
};
