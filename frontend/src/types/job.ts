export interface JobItem {
  id: string;
  title: string;
  company: string;
  domain: string;
  category: string;
  seniority: string;
  location: string;
  country: string;
  is_remote: boolean;
  date_posted: string;
  apply_url: string;
  source_ats: string;
  description_summary: string;
  tags: string[];
}

export interface ParsedQuery {
  category: string | null;
  seniority: string | null;
  country: string | null;
  is_remote: boolean | null;
  domain: string | null;
  posted_within_days: number | null;
  search_terms: string | null;
  model_provider: string;
}

export interface NLPSearchResponse {
  query: string;
  parsed: ParsedQuery;
  count: number;
  jobs: JobItem[];
}

export interface Category {
  id: string;
  label: string;
  description: string;
  icon: string;
  curated_tracks: string[];
  related_skills: string[];
}

export interface DiscoveryTrack {
  track: string;
  category_id: string;
  category_label: string;
}

export interface FilterState {
  searchPrompt: string;
  category: string;
  domain: string;
  country: string;
  company?: string;
  metroHub?: string;
  isRemote: boolean | null;
  seniority: string;
  freshnessDays: number | null;
  sortBy: 'date' | 'company' | 'title';
  savedOnly: boolean;
}

export interface RedditThreadItem {
  title: string;
  url: string;
  score: number;
  num_comments: number;
  author: string;
  subreddit: string;
}

export interface CommunityInsights {
  company: string;
  role: string;
  subreddit: string;
  turnaround_estimate: string;
  interview_stages: string[];
  insider_tips: string[];
  sentiment_summary: string;
  threads: RedditThreadItem[];
  last_updated: string;
}

export interface CandidateLeadInput {
  job_id: string;
  company: string;
  role_title: string;
  candidate_name: string;
  email: string;
  linkedin_url?: string;
  yoe: number;
  current_ctc_lpa?: number;
  expected_ctc_lpa?: number;
  notice_period_days: number;
  resume_url?: string;
}

export interface CandidateLeadRecord extends CandidateLeadInput {
  id: string;
  status: string;
  created_at: string;
}

export interface LeadSubmitResult {
  success: boolean;
  lead_id: string;
  message: string;
  referral_pitch: string;
  lead: CandidateLeadRecord;
}

export interface CareerTarget {
  id: string;
  name: string;
  slug: string;
  website?: string | null;
  career_url: string;
  ats_type: string;
  feed_url?: string | null;
  category_tier: string;
  domain: string;
  role_focus: string[];
  status: string;
  last_scraped_at?: string | null;
  last_status?: string | null;
  job_count: number;
  created_at: string;
}

export interface CareerTargetStats {
  total_targets: number;
  active_targets: number;
  by_tier: Record<string, number>;
  total_live_jobs: number;
}

export interface BatchSyncStatus {
  is_running: boolean;
  current_target?: string | null;
  completed: number;
  total: number;
  progress_percent: number;
  last_run_timestamp?: string | null;
  last_run_duration_sec?: number | null;
  last_error?: string | null;
}

export interface TargetFilterParams {
  tier?: string;
  domain?: string;
  role_tag?: string;
  status?: string;
  search?: string;
  limit?: number;
  offset?: number;
}


