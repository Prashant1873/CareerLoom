import React from 'react';
import { ExternalLink, Bookmark, MapPin, Building2, Calendar, Zap, MessageSquare } from 'lucide-react';
import type { JobItem } from '../types/job';
import { formatJobDate } from '../utils/dateFormatter';
import { getCTCInfo } from '../utils/ctcFormatter';

interface JobCardProps {
  job: JobItem;
  isBookmarked: boolean;
  onToggleBookmark: (id: string) => void;
  onSelectJob: (job: JobItem) => void;
  onOpenInsights?: (job: JobItem) => void;
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  isBookmarked,
  onToggleBookmark,
  onSelectJob,
  onOpenInsights,
}) => {
  const { relative, exact, tier } = formatJobDate(job.date_posted);
  const ctcInfo = getCTCInfo(
    job.company,
    job.title,
    job.country,
    job.location,
    job.seniority,
    job.category,
    job.tags,
    job.description_summary
  );

  const handleApplyClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    window.open(job.apply_url, '_blank', 'noopener,noreferrer');
  };

  const handleBookmarkClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleBookmark(job.id);
  };

  return (
    <article
      className="job-card"
      onClick={() => onSelectJob(job)}
      tabIndex={0}
      role="button"
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelectJob(job);
        }
      }}
      aria-label={`${job.title} at ${job.company}`}
    >
      {/* Top Meta Row */}
      <div className="card-top-row">
        <div className="company-info">
          <div className="company-logo-placeholder">
            <Building2 size={16} />
          </div>
          <div>
            <span className="company-name">{job.company}</span>
            {job.domain && <span className="domain-pill">{job.domain}</span>}
          </div>
        </div>

        {/* Prominent Posting Date Badge (UI-03) */}
        <div className={`date-badge tier-${tier}`} title={`Posted on ${exact}`}>
          <Calendar size={12} className="date-icon" />
          <span className="date-relative">{relative}</span>
          <span className="date-exact">{exact}</span>
        </div>
      </div>

      {/* Job Title */}
      <h3 className="job-title" title={job.title}>
        {job.title}
      </h3>

      {/* Location & Attributes */}
      <div className="card-attributes">
        <div className="attribute-item location">
          <MapPin size={13} />
          <span className="attribute-text">{job.location || 'Multiple Locations'}</span>
        </div>

        {job.is_remote && (
          <span className="remote-pill">
            <Zap size={11} /> Remote
          </span>
        )}

        {job.seniority && (
          <span className="seniority-pill">
            {job.seniority.charAt(0).toUpperCase() + job.seniority.slice(1)}
          </span>
        )}

        {ctcInfo && (
          <span
            className={`ctc-compensation-pill ${ctcInfo.isEstimated ? 'estimated' : 'verified'}`}
            title={ctcInfo.benchmarkDetails || ctcInfo.tierBadge}
          >
            <span className="ctc-pill-value">{ctcInfo.display}</span>
            <span className="ctc-pill-badge">{ctcInfo.tierBadge}</span>
          </span>
        )}
      </div>

      {/* Description Snippet */}
      {job.description_summary && (
        <p className="card-summary">{job.description_summary}</p>
      )}

      {/* Tags */}
      {job.tags && job.tags.length > 0 && (
        <div className="card-tags">
          {job.tags.slice(0, 4).map((tag, idx) => (
            <span key={idx} className="skill-tag">
              {tag}
            </span>
          ))}
          {job.tags.length > 4 && (
            <span className="skill-tag-overflow">+{job.tags.length - 4}</span>
          )}
        </div>
      )}

      {/* Action Footer */}
      <div className="card-footer">
        <div className="card-footer-left">
          <button
            type="button"
            className={`bookmark-btn ${isBookmarked ? 'bookmarked' : ''}`}
            onClick={handleBookmarkClick}
            title={isBookmarked ? 'Remove bookmark' : 'Bookmark this job'}
            aria-label={isBookmarked ? 'Remove bookmark' : 'Bookmark this job'}
          >
            <Bookmark size={15} fill={isBookmarked ? 'currentColor' : 'none'} />
          </button>

          {onOpenInsights && (
            <button
              type="button"
              className="insights-trigger-btn"
              onClick={(e) => {
                e.stopPropagation();
                onOpenInsights(job);
              }}
              title="View interview stages, timelines & Reddit discussions"
            >
              <MessageSquare size={13} className="text-orange-400" />
              <span>Intel</span>
            </button>
          )}
        </div>

        <button
          type="button"
          className="apply-cta-btn"
          onClick={handleApplyClick}
          title="Apply on official company portal"
        >
          <span>Apply</span>
          <ExternalLink size={13} className="cta-icon" />
        </button>
      </div>
    </article>
  );
};

