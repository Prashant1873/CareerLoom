import React, { useState, useEffect } from 'react';
import {
  Building2,
  MapPin,
  Calendar,
  Globe,
  ShieldCheck,
  ExternalLink,
  Bookmark,
  Share2,
  Clock,
  Sparkles,
  CheckCircle2,
  Lightbulb,
  MessageSquare,
  ThumbsUp,
  MessageCircle,
  RefreshCw,
  X,
  Briefcase,
} from 'lucide-react';
import type { CommunityInsights, JobItem } from '../types/job';
import { formatJobDate } from '../utils/dateFormatter';
import { fetchCommunityInsights } from '../services/api';

interface JobInspectorPaneProps {
  job: JobItem | null;
  isBookmarked: boolean;
  onToggleBookmark: (id: string) => void;
  onClose?: () => void;
  isMobileDrawer?: boolean;
}

export const JobInspectorPane: React.FC<JobInspectorPaneProps> = ({
  job,
  isBookmarked,
  onToggleBookmark,
  onClose,
  isMobileDrawer = false,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'intel'>('overview');
  const [insights, setInsights] = useState<CommunityInsights | null>(null);
  const [isIntelLoading, setIsIntelLoading] = useState<boolean>(false);
  const [copiedLink, setCopiedLink] = useState<boolean>(false);

  // Load insights whenever selected job changes
  useEffect(() => {
    if (!job) {
      setInsights(null);
      return;
    }

    let isMounted = true;
    async function loadInsights() {
      if (!job) return;
      setIsIntelLoading(true);
      try {
        const data = await fetchCommunityInsights(job.company, job.title, job.domain);
        if (isMounted) setInsights(data);
      } catch (err) {
        console.error('Failed loading intel:', err);
      } finally {
        if (isMounted) setIsIntelLoading(false);
      }
    }

    loadInsights();
    return () => {
      isMounted = false;
    };
  }, [job]);

  if (!job) {
    return (
      <aside className={`inspector-pane empty-state ${isMobileDrawer ? 'mobile-drawer' : ''}`}>
        <div className="inspector-placeholder">
          <div className="placeholder-icon-ring">
            <Briefcase size={28} className="text-zinc-600" />
          </div>
          <h3 className="placeholder-title">No Opportunity Selected</h3>
          <p className="placeholder-desc">
            Click on any job card in the stream or use <kbd>J</kbd> / <kbd>K</kbd> to inspect verified listings and Reddit interview debriefs.
          </p>
        </div>
      </aside>
    );
  }

  const { relative, exact, tier } = formatJobDate(job.date_posted);

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(job.apply_url);
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2000);
    }
  };

  return (
    <aside className={`inspector-pane ${isMobileDrawer ? 'mobile-drawer open' : ''}`}>
      {/* Inspector Header */}
      <div className="inspector-header">
        <div className="header-meta-row">
          <div className="company-badge-wrap">
            <div className="company-logo-square">
              <Building2 size={20} />
            </div>
            <div>
              <div className="company-name-row">
                <span className="inspector-company">{job.company}</span>
                {job.domain && <span className="inspector-domain">{job.domain}</span>}
              </div>
              <span className="ats-verified-tag">
                <ShieldCheck size={11} /> Verified {job.source_ats || 'ATS'}
              </span>
            </div>
          </div>

          <div className="header-actions-right">
            <button
              type="button"
              className="share-btn"
              onClick={handleShare}
              title={copiedLink ? 'Link copied to clipboard!' : 'Copy application link'}
            >
              <Share2 size={15} />
              {copiedLink && <span className="copied-tooltip">Copied!</span>}
            </button>

            {onClose && (
              <button
                type="button"
                className="inspector-close-btn"
                onClick={onClose}
                aria-label="Close details"
              >
                <X size={18} />
              </button>
            )}
          </div>
        </div>

        {/* Title */}
        <h2 className="inspector-job-title">{job.title}</h2>

        {/* Top CTA Row */}
        <div className="inspector-cta-row">
          <button
            type="button"
            className="inspector-apply-btn"
            onClick={() => window.open(job.apply_url, '_blank', 'noopener,noreferrer')}
            title="Open official career portal"
          >
            <span>Apply on Company Site</span>
            <ExternalLink size={14} />
          </button>

          <button
            type="button"
            className={`inspector-bookmark-btn ${isBookmarked ? 'bookmarked' : ''}`}
            onClick={() => onToggleBookmark(job.id)}
            title={isBookmarked ? 'Remove from saved' : 'Save opportunity (S)'}
          >
            <Bookmark size={16} fill={isBookmarked ? 'currentColor' : 'none'} />
            <span>{isBookmarked ? 'Saved' : 'Save'}</span>
          </button>
        </div>

        {/* Meta Grid */}
        <div className="inspector-meta-grid">
          <div className="meta-tile">
            <MapPin size={13} className="tile-icon" />
            <div>
              <span className="tile-label">Location</span>
              <span className="tile-val">{job.location || 'Multiple Locations'}</span>
            </div>
          </div>

          <div className="meta-tile">
            <Calendar size={13} className="tile-icon" />
            <div>
              <span className="tile-label">Posted</span>
              <div className="tile-date-row">
                <span className={`date-tier-pill tier-${tier}`}>{relative}</span>
                <span className="tile-val-sub">{exact}</span>
              </div>
            </div>
          </div>

          <div className="meta-tile">
            <Globe size={13} className="tile-icon" />
            <div>
              <span className="tile-label">Workplace</span>
              <span className="tile-val">{job.is_remote ? 'Remote' : 'Onsite / Hybrid'}</span>
            </div>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="inspector-tabs-nav">
          <button
            type="button"
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Role Overview
          </button>
          <button
            type="button"
            className={`tab-btn ${activeTab === 'intel' ? 'active' : ''}`}
            onClick={() => setActiveTab('intel')}
          >
            <span className="tab-label-flex">
              Reddit Intel
              {insights && <span className="tab-pill-mini">Live</span>}
            </span>
          </button>
        </div>
      </div>

      {/* Inspector Scrollable Content */}
      <div className="inspector-body">
        {activeTab === 'overview' && (
          <div className="overview-tab-content animate-fade-in">
            <div className="content-section">
              <h4 className="section-heading">Description Summary</h4>
              <p className="description-text">
                {job.description_summary ||
                  'Discover this verified opening directly from the employer career portal. Direct ATS verification ensures zero intermediary latency and clean application submission.'}
              </p>
            </div>

            {job.tags && job.tags.length > 0 && (
              <div className="content-section">
                <h4 className="section-heading">Skills & Keywords</h4>
                <div className="tags-flex-wrap">
                  {job.tags.map((tag, idx) => (
                    <span key={idx} className="inspector-tag-pill">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'intel' && (
          <div className="intel-tab-content animate-fade-in">
            {isIntelLoading ? (
              <div className="intel-loading-wrap">
                <RefreshCw size={24} className="animate-spin text-emerald-400 mb-2" />
                <span className="loading-txt">Aggregating Reddit debriefs & timelines...</span>
              </div>
            ) : insights ? (
              <>
                {/* Hero Intel Card */}
                <div className="intel-hero-card">
                  <div className="intel-stat-item">
                    <div className="stat-label">
                      <Clock size={12} className="text-emerald-400" />
                      <span>Avg. Turnaround</span>
                    </div>
                    <span className="stat-highlight">{insights.turnaround_estimate}</span>
                  </div>

                  <div className="intel-sentiment-item">
                    <div className="stat-label">
                      <Sparkles size={12} className="text-amber-400" />
                      <span>Hiring Consensus</span>
                    </div>
                    <p className="sentiment-snippet">{insights.sentiment_summary}</p>
                  </div>
                </div>

                {/* Interview Process Roadmap */}
                {insights.interview_stages && insights.interview_stages.length > 0 && (
                  <div className="content-section">
                    <h4 className="section-heading">
                      <CheckCircle2 size={14} className="text-emerald-400" />
                      Interview Process Roadmap
                    </h4>
                    <div className="inspector-stages-list">
                      {insights.interview_stages.map((stage, idx) => (
                        <div key={idx} className="inspector-stage-node">
                          <div className="node-number">{idx + 1}</div>
                          <div className="node-card">
                            <span className="node-title">{stage}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Insider Tips */}
                {insights.insider_tips && insights.insider_tips.length > 0 && (
                  <div className="content-section">
                    <h4 className="section-heading">
                      <Lightbulb size={14} className="text-amber-400" />
                      Candidate Insider Tips
                    </h4>
                    <div className="inspector-tips-list">
                      {insights.insider_tips.map((tip, idx) => (
                        <div key={idx} className="inspector-tip-card">
                          <span className="tip-dot">•</span>
                          <p className="tip-body">{tip}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Reddit Discussion Links */}
                {insights.threads && insights.threads.length > 0 && (
                  <div className="content-section">
                    <h4 className="section-heading">
                      <MessageSquare size={14} className="text-orange-400" />
                      Public Reddit Discussions ({insights.threads.length})
                    </h4>
                    <div className="inspector-threads-list">
                      {insights.threads.map((t, idx) => (
                        <a
                          key={idx}
                          href={t.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inspector-thread-card"
                        >
                          <div className="thread-title-flex">
                            <span className="thread-heading">{t.title}</span>
                            <ExternalLink size={12} className="thread-open-icon" />
                          </div>
                          <div className="thread-meta-flex">
                            <span className="thread-sub-name">r/{t.subreddit}</span>
                            <div className="thread-counters">
                              <span>
                                <ThumbsUp size={10} /> {t.score}
                              </span>
                              <span>
                                <MessageCircle size={10} /> {t.num_comments}
                              </span>
                            </div>
                          </div>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="intel-empty-wrap">
                <MessageSquare size={28} className="text-zinc-600 mb-2" />
                <p>No community debriefs available for this employer.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  );
};
