import React, { useEffect, useState } from 'react';
import {
  X,
  ExternalLink,
  Clock,
  CheckCircle2,
  Lightbulb,
  MessageSquare,
  MessageCircle,
  ThumbsUp,
  Building2,
  Sparkles,
  RefreshCw,
} from 'lucide-react';
import type { CommunityInsights, JobItem } from '../types/job';
import { fetchCommunityInsights } from '../services/api';

interface CommunityInsightsDrawerProps {
  job: JobItem | null;
  isOpen: boolean;
  onClose: () => void;
}

export const CommunityInsightsDrawer: React.FC<CommunityInsightsDrawerProps> = ({
  job,
  isOpen,
  onClose,
}) => {
  const [insights, setInsights] = useState<CommunityInsights | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  useEffect(() => {
    if (!isOpen || !job) {
      setInsights(null);
      return;
    }

    let isMounted = true;
    async function loadData() {
      if (!job) return;
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchCommunityInsights(job.company, job.title, job.domain, job.country);
        if (isMounted) {
          if (data) {
            setInsights(data);
          } else {
            setError('Could not retrieve community intelligence for this employer.');
          }
        }
      } catch (err) {
        if (isMounted) {
          setError('Failed to connect to community insights service.');
        }
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    loadData();

    return () => {
      isMounted = false;
    };
  }, [isOpen, job]);

  if (!isOpen && !job) return null;

  return (
    <div
      className={`drawer-backdrop ${isOpen ? 'open' : ''}`}
      onClick={onClose}
      aria-hidden={!isOpen}
      role="dialog"
      aria-modal="true"
    >
      <div
        className={`drawer-container ${isOpen ? 'open' : ''}`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div className="drawer-header">
          <div className="drawer-title-group">
            <div className="drawer-brand-icon">
              <Building2 size={20} />
            </div>
            <div>
              <div className="drawer-subhead">
                <span>Community Intel</span>
                {insights?.subreddit && (
                  <span className="subreddit-badge">
                    {insights.subreddit.toLowerCase().includes('developersindia') && '🇮🇳 '}
                    {insights.subreddit.startsWith('r/') ? insights.subreddit : `r/${insights.subreddit}`}
                  </span>
                )}
              </div>
              <h2 className="drawer-company-title">{job?.company}</h2>
            </div>
          </div>

          <button
            type="button"
            className="drawer-close-btn"
            onClick={onClose}
            aria-label="Close community insights"
          >
            <X size={18} />
          </button>
        </div>

        {/* Drawer Body */}
        <div className="drawer-body">
          {isLoading && (
            <div className="drawer-loading-state">
              <RefreshCw className="animate-spin text-emerald-400" size={28} />
              <p className="loading-text">Mining Reddit discussions & interview consensus...</p>
              <span className="loading-subtext">Aggregating timeline estimates and candidate debriefs</span>
            </div>
          )}

          {error && !isLoading && (
            <div className="drawer-error-state">
              <MessageSquare size={32} className="error-icon" />
              <p className="error-message">{error}</p>
            </div>
          )}

          {!isLoading && insights && (
            <>
              {/* Highlight Stats Banner */}
              <div className="insights-hero-banner">
                <div className="hero-stat-box">
                  <div className="stat-label-row">
                    <Clock size={14} className="stat-icon-emerald" />
                    <span>Average Turnaround</span>
                  </div>
                  <div className="stat-value-highlight">
                    {insights.turnaround_estimate}
                  </div>
                </div>

                <div className="hero-summary-box">
                  <div className="summary-title-row">
                    <Sparkles size={14} className="stat-icon-amber" />
                    <span>Hiring Sentiment</span>
                  </div>
                  <p className="summary-content">{insights.sentiment_summary}</p>
                </div>
              </div>

              {/* Interview Process Roadmap */}
              {insights.interview_stages && insights.interview_stages.length > 0 && (
                <section className="drawer-section">
                  <h3 className="drawer-section-title">
                    <CheckCircle2 size={16} className="section-header-icon" />
                    Interview Process & Stages
                  </h3>
                  <div className="timeline-stages">
                    {insights.interview_stages.map((stage, idx) => (
                      <div key={idx} className="timeline-stage-item">
                        <div className="stage-marker">
                          <span className="stage-number">{idx + 1}</span>
                          {idx < insights.interview_stages.length - 1 && (
                            <div className="stage-connector" />
                          )}
                        </div>
                        <div className="stage-card">
                          <span className="stage-name">{stage}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Candidate Insider Tips */}
              {insights.insider_tips && insights.insider_tips.length > 0 && (
                <section className="drawer-section">
                  <h3 className="drawer-section-title">
                    <Lightbulb size={16} className="section-header-icon-amber" />
                    Candidate Insider Tips
                  </h3>
                  <div className="insider-tips-list">
                    {insights.insider_tips.map((tip, idx) => (
                      <div key={idx} className="tip-card">
                        <span className="tip-bullet">•</span>
                        <p className="tip-text">{tip}</p>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Verified Reddit Discussions */}
              {insights.threads && insights.threads.length > 0 && (
                <section className="drawer-section">
                  <h3 className="drawer-section-title">
                    <MessageSquare size={16} className="section-header-icon-orange" />
                    Recent Reddit Discussions ({insights.threads.length})
                  </h3>
                  <div className="reddit-threads-list">
                    {insights.threads.map((thread, idx) => (
                      <a
                        key={idx}
                        href={thread.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="reddit-thread-card"
                      >
                        <div className="thread-title-row">
                          <h4 className="thread-title">{thread.title}</h4>
                          <ExternalLink size={13} className="thread-link-icon" />
                        </div>
                        <div className="thread-meta-row">
                          <span className="thread-sub">
                            {thread.subreddit.startsWith('r/') ? thread.subreddit : `r/${thread.subreddit}`}
                          </span>
                          <span className="thread-author">by {thread.author}</span>
                          <div className="thread-stats">
                            <span className="thread-upvotes">
                              <ThumbsUp size={11} /> {thread.score}
                            </span>
                            <span className="thread-comments">
                              <MessageCircle size={11} /> {thread.num_comments}
                            </span>
                          </div>
                        </div>
                      </a>
                    ))}
                  </div>
                </section>
              )}
            </>
          )}
        </div>

        {/* Drawer Footer */}
        <div className="drawer-footer">
          <p className="drawer-disclaimer">
            Information aggregated from public discussions and candidate debriefs. Timelines may vary by department and geography.
          </p>
        </div>
      </div>
    </div>
  );
};
