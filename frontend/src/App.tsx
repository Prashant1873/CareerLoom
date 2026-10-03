import { useState, useEffect, useCallback } from 'react';
import './App.css';
import type { Category, DiscoveryTrack, FilterState, JobItem, ParsedQuery } from './types/job';
import { fetchCategories, fetchDiscoveryTracks, nlpSearch, searchJobs } from './services/api';
import { useBookmarks } from './hooks/useBookmarks';
import { Header } from './components/Header';
import { SearchBar } from './components/SearchBar';
import { CategoryPills } from './components/CategoryPills';
import { FilterSidebar } from './components/FilterSidebar';
import { JobGrid } from './components/JobGrid';
import { JobDetailModal } from './components/JobDetailModal';

const DEFAULT_FILTERS: FilterState = {
  searchPrompt: '',
  category: '',
  domain: '',
  country: '',
  isRemote: null,
  seniority: '',
  freshnessDays: null,
  sortBy: 'date',
  savedOnly: false,
};

export function App() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [tracks, setTracks] = useState<DiscoveryTrack[]>([]);
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [parsedQuery, setParsedQuery] = useState<ParsedQuery | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobItem | null>(null);
  const [totalJobsIndexed, setTotalJobsIndexed] = useState<number>(0);

  const { savedIds, savedCount, isBookmarked, toggleBookmark } = useBookmarks();

  // Load initial taxonomy & metadata on mount
  useEffect(() => {
    async function loadMeta() {
      try {
        const [cats, trks, allJobs] = await Promise.all([
          fetchCategories(),
          fetchDiscoveryTracks(),
          searchJobs({ limit: 100 }),
        ]);
        setCategories(cats);
        setTracks(trks);
        setTotalJobsIndexed(allJobs.length > 0 ? allJobs.length : 1000);
      } catch (e) {
        console.error('Error loading metadata:', e);
      }
    }
    loadMeta();
  }, []);

  // Perform search whenever searchPrompt or structured filters change
  const executeSearch = useCallback(
    async (currentFilters: FilterState) => {
      setIsLoading(true);
      try {
        if (currentFilters.searchPrompt.trim()) {
          // Conversational search via NLP engine
          const response = await nlpSearch(currentFilters.searchPrompt, {
            category: currentFilters.category || undefined,
            domain: currentFilters.domain || undefined,
            country: currentFilters.country || undefined,
            is_remote: currentFilters.isRemote !== null ? currentFilters.isRemote : undefined,
            seniority: currentFilters.seniority || undefined,
            posted_within_days: currentFilters.freshnessDays || undefined,
            sort_by: currentFilters.sortBy,
            limit: 100,
          });
          setParsedQuery(response.parsed);
          setJobs(response.jobs);
        } else {
          // Standard multi-faceted search
          setParsedQuery(null);
          const results = await searchJobs({
            category: currentFilters.category || undefined,
            domain: currentFilters.domain || undefined,
            country: currentFilters.country || undefined,
            is_remote: currentFilters.isRemote !== null ? currentFilters.isRemote : undefined,
            seniority: currentFilters.seniority || undefined,
            posted_within_days: currentFilters.freshnessDays || undefined,
            sort_by: currentFilters.sortBy,
            limit: 100,
          });
          setJobs(results);
        }
      } catch (err) {
        console.error('Failed search execution:', err);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    executeSearch(filters);
  }, [filters, executeSearch]);

  const handleQueryChange = (query: string) => {
    setFilters((prev) => ({ ...prev, searchPrompt: query }));
  };

  const handleSearchSubmit = (query: string) => {
    const updated = { ...filters, searchPrompt: query };
    setFilters(updated);
    executeSearch(updated);
  };

  const handleSelectCategory = (categoryId: string) => {
    setFilters((prev) => ({
      ...prev,
      category: categoryId,
      // If prompt was empty, clearing category resets cleanly
    }));
  };

  const handleSelectTrack = (track: DiscoveryTrack) => {
    setFilters((prev) => ({
      ...prev,
      searchPrompt: track.track,
      category: track.category_id,
    }));
  };

  const handleFilterChange = (partial: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...partial }));
  };

  const handleResetFilters = () => {
    setFilters(DEFAULT_FILTERS);
  };

  const handleToggleSavedOnly = () => {
    setFilters((prev) => ({ ...prev, savedOnly: !prev.savedOnly }));
  };

  // Filter jobs by saved status if savedOnly is enabled
  const displayedJobs = filters.savedOnly
    ? jobs.filter((j) => savedIds.includes(j.id))
    : jobs;

  const hasActiveFilters = Boolean(
    filters.searchPrompt ||
      filters.category ||
      filters.domain ||
      filters.country ||
      filters.isRemote !== null ||
      filters.seniority ||
      filters.freshnessDays !== null
  );

  return (
    <div className="app-container">
      <Header
        savedCount={savedCount}
        showSavedOnly={filters.savedOnly}
        onToggleSavedOnly={handleToggleSavedOnly}
        totalJobs={totalJobsIndexed}
      />

      <main className="main-wrapper">
        <SearchBar
          query={filters.searchPrompt}
          onQueryChange={handleQueryChange}
          onSearch={handleSearchSubmit}
          isLoading={isLoading}
          parsedQuery={parsedQuery}
        />

        <CategoryPills
          categories={categories}
          tracks={tracks}
          selectedCategory={filters.category}
          onSelectCategory={handleSelectCategory}
          onSelectTrack={handleSelectTrack}
        />

        <div className="content-layout">
          <FilterSidebar
            filters={filters}
            onFilterChange={handleFilterChange}
            onResetFilters={handleResetFilters}
            totalFilteredCount={displayedJobs.length}
          />

          <section className="results-area">
            <div className="results-meta-bar">
              <span className="results-count-text">
                {filters.savedOnly ? (
                  <>Showing <span className="count-highlight">{displayedJobs.length}</span> saved opportunities</>
                ) : (
                  <>Found <span className="count-highlight">{displayedJobs.length}</span> verified postings</>
                )}
              </span>
            </div>

            <JobGrid
              jobs={displayedJobs}
              isLoading={isLoading}
              isBookmarked={isBookmarked}
              onToggleBookmark={toggleBookmark}
              onSelectJob={setSelectedJob}
              onResetFilters={handleResetFilters}
              hasActiveFilters={hasActiveFilters}
              isSavedTab={filters.savedOnly}
            />
          </section>
        </div>
      </main>

      <JobDetailModal
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
        isBookmarked={selectedJob ? isBookmarked(selectedJob.id) : false}
        onToggleBookmark={toggleBookmark}
      />
    </div>
  );
}

export default App;
