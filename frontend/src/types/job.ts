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
  isRemote: boolean | null;
  seniority: string;
  freshnessDays: number | null;
  sortBy: 'date' | 'company' | 'title';
  savedOnly: boolean;
}
