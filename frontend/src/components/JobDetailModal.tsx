import React, { useEffect } from 'react';
import { X, ExternalLink, Bookmark, MapPin, Building2, Calendar, ShieldCheck, Globe } from 'lucide-react';
import type { JobItem } from '../types/job';
import { formatJobDate } from '../utils/dateFormatter';

interface JobDetailModalProps {
  job: JobItem | null;
  onClose: () => void;
  isBookmarked: boolean;
  onToggleBookmark: (id: string) => void;
}

export const JobDetailModal: React.FC<JobDetailModalProps> = ({
  job,
  onClose,
  isBookmarked,
  onToggleBookmark,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (job) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [job, onClose]);

  if (!job) return null;

  const { relative, exact, tier } = formatJobDate(job.date_posted);

  const handleApply = () => {
    window.open(job.apply_url, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-card animate-fade-in" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-group">
            <div className="company-logo-large">
              <Building2 size={24} />
            </div>
            <div>
              <div className="modal-company-row">
                <span className="modal-company">{job.company}</span>
                {job.domain && <span className="domain-pill">{job.domain}</span>}
                <span className="verified-badge">
                  <ShieldCheck size={12} /> Verified ATS
                </span>
              </div>
              <h2 className="modal-job-title">{job.title}</h2>
            </div>
          </div>

          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close modal"
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Meta Bar */}
        <div className="modal-meta-grid">
          <div className="meta-box">
            <MapPin size={16} className="meta-icon" />
            <div>
              <span className="meta-label">Location</span>
              <span className="meta-val">{job.location || 'Multiple Locations'}</span>
            </div>
          </div>

          <div className="meta-box">
            <Calendar size={16} className="meta-icon" />
            <div>
              <span className="meta-label">Date Posted</span>
              <div className="meta-date-row">
                <span className={`date-pill-mini tier-${tier}`}>{relative}</span>
                <span className="meta-val">{exact}</span>
              </div>
            </div>
          </div>

          <div className="meta-box">
            <Globe size={16} className="meta-icon" />
            <div>
              <span className="meta-label">Work Mode</span>
              <span className="meta-val">{job.is_remote ? 'Remote' : 'Onsite / Hybrid'}</span>
            </div>
          </div>
        </div>

        {/* Modal Body / Description */}
        <div className="modal-body">
          <h4 className="section-title">Role Summary</h4>
          <p className="modal-description">
            {job.description_summary ||
              'Explore this verified opening directly on the official employer career portal.'}
          </p>

          {job.tags && job.tags.length > 0 && (
            <div className="modal-skills-section">
              <h4 className="section-title">Skills & Keywords</h4>
              <div className="skills-wrap">
                {job.tags.map((tag, idx) => (
                  <span key={idx} className="skill-tag-modal">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Modal Actions Footer */}
        <div className="modal-footer">
          <button
            type="button"
            className={`modal-bookmark-btn ${isBookmarked ? 'bookmarked' : ''}`}
            onClick={() => onToggleBookmark(job.id)}
            aria-label={isBookmarked ? 'Saved to bookmarks' : 'Save to bookmarks'}
          >
            <Bookmark size={18} fill={isBookmarked ? 'currentColor' : 'none'} />
            <span>{isBookmarked ? 'Saved' : 'Save Job'}</span>
          </button>

          <button
            type="button"
            className="modal-apply-btn"
            onClick={handleApply}
            title="Open official ATS career application"
          >
            <span>Apply on Official Portal</span>
            <ExternalLink size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};
