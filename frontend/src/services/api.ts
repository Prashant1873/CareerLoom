import type { Category, DiscoveryTrack, JobItem, NLPSearchResponse, ParsedQuery } from '../types/job';

const API_BASE = '/api';

export async function fetchCategories(): Promise<Category[]> {
  try {
    const res = await fetch(`${API_BASE}/categories`);
    if (!res.ok) throw new Error(`Failed to fetch categories: ${res.statusText}`);
    const data = await res.json();
    return data.categories || [];
  } catch (err) {
    console.error('Error in fetchCategories:', err);
    return [];
  }
}

export async function fetchDiscoveryTracks(): Promise<DiscoveryTrack[]> {
  try {
    const res = await fetch(`${API_BASE}/categories/tracks`);
    if (!res.ok) throw new Error(`Failed to fetch discovery tracks: ${res.statusText}`);
    const data = await res.json();
    return data.tracks || [];
  } catch (err) {
    console.error('Error in fetchDiscoveryTracks:', err);
    return [];
  }
}

export async function parseQuery(prompt: string): Promise<ParsedQuery | null> {
  try {
    const res = await fetch(`${API_BASE}/nlp/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    if (!res.ok) throw new Error(`Failed to parse query: ${res.statusText}`);
    const data = await res.json();
    return data.parsed_parameters;
  } catch (err) {
    console.error('Error in parseQuery:', err);
    return null;
  }
}

export interface SearchParams {
  category?: string;
  domain?: string;
  country?: string;
  is_remote?: boolean;
  seniority?: string;
  posted_within_days?: number;
  keyword?: string;
  sort_by?: 'date' | 'company' | 'title';
  limit?: number;
  offset?: number;
}

export async function searchJobs(params: SearchParams = {}): Promise<JobItem[]> {
  try {
    const queryParams = new URLSearchParams();
    if (params.category) queryParams.set('category', params.category);
    if (params.domain) queryParams.set('domain', params.domain);
    if (params.country) queryParams.set('country', params.country);
    if (typeof params.is_remote === 'boolean') queryParams.set('is_remote', String(params.is_remote));
    if (params.seniority) queryParams.set('seniority', params.seniority);
    if (params.posted_within_days) queryParams.set('posted_within_days', String(params.posted_within_days));
    if (params.keyword) queryParams.set('keyword', params.keyword);
    if (params.sort_by) queryParams.set('sort_by', params.sort_by);
    if (params.limit) queryParams.set('limit', String(params.limit));
    if (params.offset) queryParams.set('offset', String(params.offset));

    const res = await fetch(`${API_BASE}/jobs?${queryParams.toString()}`);
    if (!res.ok) throw new Error(`Failed to search jobs: ${res.statusText}`);
    const data = await res.json();
    return data.jobs || [];
  } catch (err) {
    console.error('Error in searchJobs:', err);
    return [];
  }
}

export async function nlpSearch(
  query: string,
  overrides: {
    category?: string;
    domain?: string;
    country?: string;
    is_remote?: boolean;
    seniority?: string;
    posted_within_days?: number;
    sort_by?: 'date' | 'company' | 'title';
    limit?: number;
  } = {}
): Promise<NLPSearchResponse> {
  try {
    const res = await fetch(`${API_BASE}/nlp/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: query,
        sort_by: overrides.sort_by || 'date',
        limit: overrides.limit ?? 100,
      }),
    });
    if (!res.ok) throw new Error(`Failed in nlpSearch: ${res.statusText}`);
    const data = await res.json();
    return {
      query: data.prompt,
      parsed: data.parsed_parameters,
      count: data.total,
      jobs: data.jobs || [],
    };
  } catch (err) {
    console.error('Error in nlpSearch:', err);
    return {
      query,
      parsed: {
        category: null,
        seniority: null,
        country: null,
        is_remote: null,
        domain: null,
        posted_within_days: null,
        search_terms: null,
        model_provider: 'fallback',
      },
      count: 0,
      jobs: [],
    };
  }
}

export async function fetchCommunityInsights(
  company: string,
  role?: string,
  domain?: string
): Promise<import('../types/job').CommunityInsights | null> {
  try {
    const params = new URLSearchParams({ company });
    if (role) params.set('role', role);
    if (domain) params.set('domain', domain);
    const res = await fetch(`${API_BASE}/insights/company?${params.toString()}`);
    if (!res.ok) throw new Error(`Failed to fetch insights: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.error('Error fetching community insights:', err);
    return null;
  }
}

