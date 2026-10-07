import React, { useState } from 'react';
import {
  X,
  Copy,
  Check,
  Building2,
  FileText,
  Sparkles,
  ExternalLink,
  AlertCircle
} from 'lucide-react';
import type { JobItem, LeadSubmitResult } from '../types/job';
import { submitCandidateLead } from '../services/api';

const LinkedInIcon: React.FC<{ size?: number; className?: string }> = ({ size = 14, className = '' }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="currentColor"
    className={className}
    style={{ flexShrink: 0 }}
  >
    <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z" />
  </svg>
);

interface LeadCaptureModalProps {
  job: JobItem | null;
  isOpen: boolean;
  onClose: () => void;
}

export const LeadCaptureModal: React.FC<LeadCaptureModalProps> = ({
  job,
  isOpen,
  onClose,
}) => {
  const [candidateName, setCandidateName] = useState('');
  const [email, setEmail] = useState('');
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [yoe, setYoe] = useState<string>('3');
  const [currentCtc, setCurrentCtc] = useState<string>('');
  const [expectedCtc, setExpectedCtc] = useState<string>('');
  const [noticePeriod, setNoticePeriod] = useState<number>(30);
  const [resumeUrl, setResumeUrl] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [submissionResult, setSubmissionResult] = useState<LeadSubmitResult | null>(null);
  const [copiedPitch, setCopiedPitch] = useState(false);

  if (!isOpen || !job) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    const parsedYoe = parseFloat(yoe);
    if (isNaN(parsedYoe) || parsedYoe < 0) {
      setErrorMsg('Please enter valid years of experience.');
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await submitCandidateLead({
        job_id: job.id,
        company: job.company,
        role_title: job.title,
        candidate_name: candidateName.trim(),
        email: email.trim(),
        linkedin_url: linkedinUrl.trim() || undefined,
        yoe: parsedYoe,
        current_ctc_lpa: currentCtc ? parseFloat(currentCtc) : undefined,
        expected_ctc_lpa: expectedCtc ? parseFloat(expectedCtc) : undefined,
        notice_period_days: noticePeriod,
        resume_url: resumeUrl.trim() || undefined,
      });

      setSubmissionResult(result);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit candidate lead.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCopyPitch = () => {
    if (!submissionResult?.referral_pitch) return;
    navigator.clipboard.writeText(submissionResult.referral_pitch);
    setCopiedPitch(true);
    setTimeout(() => setCopiedPitch(false), 2500);
  };

  const linkedinSearchUrl = `https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(
    job.company
  )}&origin=GLOBAL_SEARCH_HEADER`;

  return (
    <div className="lead-modal-backdrop" onClick={onClose} role="dialog" aria-modal="true">
      <div className="lead-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="lead-modal-header">
          <div className="lead-header-info">
            <div className="lead-company-badge">
              <Building2 size={16} />
              <span>{job.company}</span>
            </div>
            <h3 className="lead-modal-title">
              {submissionResult ? 'Referral Request Generated!' : 'Fast Candidate Referral Engine'}
            </h3>
            <span className="lead-target-role">{job.title}</span>
          </div>

          <button
            type="button"
            className="lead-close-btn"
            onClick={onClose}
            aria-label="Close referral dialog"
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="lead-modal-body">
          {errorMsg && (
            <div className="lead-error-banner">
              <AlertCircle size={15} />
              <span>{errorMsg}</span>
            </div>
          )}

          {!submissionResult ? (
            /* Input Form */
            <form onSubmit={handleSubmit} className="lead-form">
              <p className="lead-form-hint">
                Submit your profile directly into the verified referral queue. We'll generate a tailored, high-converting pitch for alumni and current employees.
              </p>

              <div className="form-grid-two">
                <div className="form-field">
                  <label htmlFor="lead-name">Full Name *</label>
                  <input
                    id="lead-name"
                    type="text"
                    required
                    placeholder="e.g. Arjun Sharma"
                    value={candidateName}
                    onChange={(e) => setCandidateName(e.target.value)}
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="lead-email">Email Address *</label>
                  <input
                    id="lead-email"
                    type="email"
                    required
                    placeholder="arjun@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              <div className="form-grid-two">
                <div className="form-field">
                  <label htmlFor="lead-linkedin">LinkedIn Profile URL</label>
                  <div className="input-with-icon">
                    <LinkedInIcon size={14} className="field-icon" />
                    <input
                      id="lead-linkedin"
                      type="url"
                      placeholder="https://linkedin.com/in/..."
                      value={linkedinUrl}
                      onChange={(e) => setLinkedinUrl(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-field">
                  <label htmlFor="lead-yoe">Years of Experience (YoE) *</label>
                  <input
                    id="lead-yoe"
                    type="number"
                    step="0.5"
                    min="0"
                    max="40"
                    required
                    placeholder="3.5"
                    value={yoe}
                    onChange={(e) => setYoe(e.target.value)}
                  />
                </div>
              </div>

              <div className="form-grid-three">
                <div className="form-field">
                  <label htmlFor="lead-cur-ctc">Current CTC (LPA)</label>
                  <input
                    id="lead-cur-ctc"
                    type="number"
                    step="0.5"
                    min="0"
                    placeholder="e.g. 24"
                    value={currentCtc}
                    onChange={(e) => setCurrentCtc(e.target.value)}
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="lead-exp-ctc">Expected CTC (LPA)</label>
                  <input
                    id="lead-exp-ctc"
                    type="number"
                    step="0.5"
                    min="0"
                    placeholder="e.g. 38"
                    value={expectedCtc}
                    onChange={(e) => setExpectedCtc(e.target.value)}
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="lead-notice">Notice Period</label>
                  <select
                    id="lead-notice"
                    value={noticePeriod}
                    onChange={(e) => setNoticePeriod(parseInt(e.target.value, 10))}
                  >
                    <option value={0}>Immediate (0 Days)</option>
                    <option value={15}>15 Days</option>
                    <option value={30}>30 Days (1 Month)</option>
                    <option value={60}>60 Days (2 Months)</option>
                    <option value={90}>90 Days (3 Months)</option>
                  </select>
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="lead-resume">Resume Public Link (Drive / Dropbox)</label>
                <div className="input-with-icon">
                  <FileText size={14} className="field-icon" />
                  <input
                    id="lead-resume"
                    type="url"
                    placeholder="https://drive.google.com/file/d/..."
                    value={resumeUrl}
                    onChange={(e) => setResumeUrl(e.target.value)}
                  />
                </div>
              </div>

              <div className="lead-form-actions">
                <button type="button" className="lead-cancel-btn" onClick={onClose}>
                  Cancel
                </button>
                <button type="submit" className="lead-submit-btn" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <span>Registering Lead...</span>
                  ) : (
                    <>
                      <Sparkles size={15} />
                      <span>Submit Lead & Generate Pitch</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          ) : (
            /* Referral Pitch Success Card */
            <div className="lead-success-wrap animate-fade-in">
              <div className="lead-success-badge">
                <Check size={18} className="text-emerald-400" />
                <span>Profile logged into referral lead queue!</span>
              </div>

              <div className="pitch-card-container">
                <div className="pitch-card-header">
                  <span className="pitch-card-label">Your Tailored 1-Click Referral Pitch:</span>
                  <button
                    type="button"
                    className={`copy-pitch-btn ${copiedPitch ? 'copied' : ''}`}
                    onClick={handleCopyPitch}
                  >
                    {copiedPitch ? (
                      <>
                        <Check size={13} />
                        <span>Copied to Clipboard!</span>
                      </>
                    ) : (
                      <>
                        <Copy size={13} />
                        <span>Copy Pitch</span>
                      </>
                    )}
                  </button>
                </div>

                <textarea
                  readOnly
                  className="pitch-textarea"
                  value={submissionResult.referral_pitch}
                  rows={9}
                />
              </div>

              <div className="referral-sharing-guidance">
                <h5 className="guidance-title">Next Step to Secure Your Referral:</h5>
                <p className="guidance-desc">
                  Find employees or alumni working at <strong>{job.company}</strong> on LinkedIn, send a connection request, and paste this message:
                </p>
                <a
                  href={linkedinSearchUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="linkedin-search-link"
                >
                  <LinkedInIcon size={15} />
                  <span>Find {job.company} Employees on LinkedIn</span>
                  <ExternalLink size={13} />
                </a>
              </div>

              <div className="success-footer-actions">
                <button type="button" className="lead-finish-btn" onClick={onClose}>
                  Done
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
