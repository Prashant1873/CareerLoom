import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import './App.css';
import type { BatchSyncStatus, CareerTargetStats, Category, FilterState, JobItem, ParsedQuery } from './types/job';
import {
  fetchCategories,
  fetchStats,
  fetchSyncStatus,
  fetchTargetStats,
  nlpSearch,
  searchJobsWithTotal,
} from './services/api';
import { useBookmarks } from './hooks/useBookmarks';
import { useKeyboardNav } from './hooks/useKeyboardNav';
import { NavRail } from './components/NavRail';
import { MasterJobStream } from './components/MasterJobStream';
import { JobInspectorPane } from './components/JobInspectorPane';
import { CommunityInsightsDrawer } from './components/CommunityInsightsDrawer';
import { LeadCaptureModal } from './components/LeadCaptureModal';
import { CareerDirectoryModal } from './components/CareerDirectoryModal';

const DEFAULT_FILTERS: FilterState = {
  searchPrompt: '',
  category: '',
  domain: '',
  country: '',
  company: '',
  isRemote: null,
  seniority: '',
  freshnessDays: null,
  sortBy: 'date',
  savedOnly: false,
};

export function App() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [totalMatches, setTotalMatches] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [parsedQuery, setParsedQuery] = useState<ParsedQuery | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobItem | null>(null);
  const [totalJobsIndexed, setTotalJobsIndexed] = useState<number>(0);
  const [insightsJob, setInsightsJob] = useState<JobItem | null>(null);
  const [isInsightsOpen, setIsInsightsOpen] = useState<boolean>(false);
  const [referralJob, setReferralJob] = useState<JobItem | null>(null);
  const [isReferralModalOpen, setIsReferralModalOpen] = useState<boolean>(false);
  const [isRailCollapsed, setIsRailCollapsed] = useState<boolean>(false);
  const [isDirectoryOpen, setIsDirectoryOpen] = useState<boolean>(false);
  const [targetStats, setTargetStats] = useState<CareerTargetStats | null>(null);
  const [syncStatus, setSyncStatus] = useState<BatchSyncStatus | null>(null);

  const searchRef = useRef<HTMLInputElement | null>(null);
  const { savedIds, savedCount, isBookmarked, toggleBookmark } = useBookmarks();

  // Load initial taxonomy, database stats, and target stats on mount
  useEffect(() => {
    async function loadMeta() {
      try {
        const [cats, stats, tStats, sStatus] = await Promise.all([
          fetchCategories(),
          fetchStats(),
          fetchTargetStats(),
          fetchSyncStatus(),
        ]);
        setCategories(cats);
        setTotalJobsIndexed(stats.total_jobs || 16064);
        setTargetStats(tStats);
        setSyncStatus(sStatus);
      } catch (e) {
        console.error('Error loading metadata:', e);
      }
    }
    loadMeta();
  }, []);

  const [now, setNow] = useState<number>(() => Date.now());

  // Poll sync status periodically if sync is active
  useEffect(() => {
    const pollInterval = syncStatus?.is_running ? 10000 : 60000;
    const interval = setInterval(async () => {
      try {
        setNow(Date.now());
        const [sStatus, tStats] = await Promise.all([
          fetchSyncStatus(),
          fetchTargetStats(),
        ]);
        setSyncStatus(sStatus);
        setTargetStats(tStats);
      } catch (err) {
        console.error('Error polling sync status:', err);
      }
    }, pollInterval);

    return () => clearInterval(interval);
  }, [syncStatus?.is_running]);

  const syncFreshnessText = useMemo(() => {
    if (syncStatus?.is_running) return 'Syncing Now...';
    if (!syncStatus?.last_run_timestamp) return 'Feeds Active';
    try {
      const last = new Date(syncStatus.last_run_timestamp).getTime();
      const diffMin = Math.max(1, Math.round((now - last) / (1000 * 60)));
      if (diffMin < 60) return `Synced ${diffMin}m ago`;
      const diffHours = Math.round(diffMin / 60);
      if (diffHours < 24) return `Synced ${diffHours}h ago`;
      return `Synced ${Math.round(diffHours / 24)}d ago`;
    } catch {
      return 'Feeds Active';
    }
  }, [syncStatus, now]);


  // Perform search whenever searchPrompt or structured filters change
  const executeSearch = useCallback(
    async (currentFilters: FilterState) => {
      setIsLoading(true);
      try {
        if (currentFilters.searchPrompt.trim()) {
          const response = await nlpSearch(currentFilters.searchPrompt, {
            category: currentFilters.category || undefined,
            domain: currentFilters.domain || undefined,
            country: currentFilters.country || undefined,
            metro_hub: currentFilters.metroHub || undefined,
            is_remote: currentFilters.isRemote !== null ? currentFilters.isRemote : undefined,
            seniority: currentFilters.seniority || undefined,
            posted_within_days: currentFilters.freshnessDays || undefined,
            sort_by: currentFilters.sortBy,
            limit: 100,
          });
          setParsedQuery(response.parsed);
          setJobs(response.jobs);
          setTotalMatches(response.count);
          if (response.jobs.length > 0) {
            setSelectedJob(response.jobs[0]);
          }
        } else {
          setParsedQuery(null);
          const result = await searchJobsWithTotal({
            category: currentFilters.category || undefined,
            domain: currentFilters.domain || undefined,
            country: currentFilters.country || undefined,
            metro_hub: currentFilters.metroHub || undefined,
            company: currentFilters.company || undefined,
            is_remote: currentFilters.isRemote !== null ? currentFilters.isRemote : undefined,
            seniority: currentFilters.seniority || undefined,
            posted_within_days: currentFilters.freshnessDays || undefined,
            sort_by: currentFilters.sortBy,
            limit: 100,
          });
          setJobs(result.jobs);
          setTotalMatches(result.total);
          if (result.jobs.length > 0) {
            setSelectedJob(result.jobs[0]);
          }
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
    }));
  };

  const handleSelectFreshness = (days: number | null) => {
    setFilters((prev) => ({
      ...prev,
      freshnessDays: days,
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

  const handleOpenInsights = (job: JobItem) => {
    setInsightsJob(job);
    setIsInsightsOpen(true);
  };

  const handleCloseInsights = () => {
    setIsInsightsOpen(false);
  };

  const handleOpenReferral = (job: JobItem) => {
    setReferralJob(job);
    setIsReferralModalOpen(true);
  };

  // Filter jobs by saved status if savedOnly is enabled
  const displayedJobs = filters.savedOnly
    ? jobs.filter((j) => savedIds.includes(j.id))
    : jobs;

  // Keyboard navigation hook
  useKeyboardNav({
    jobs: displayedJobs,
    selectedJob,
    onSelectJob: setSelectedJob,
    onToggleBookmark: toggleBookmark,
    onFocusSearch: () => searchRef.current?.focus(),
  });

  return (
    <div className="app-v2-shell">
      {/* Column 1: Left Navigation Rail (NavRail.tsx) */}
      <NavRail
        isCollapsed={isRailCollapsed}
        onToggleCollapse={() => setIsRailCollapsed(!isRailCollapsed)}
        categories={categories}
        selectedCategory={filters.category}
        onSelectCategory={handleSelectCategory}
        totalJobsCount={totalJobsIndexed}
        savedCount={savedCount}
        showSavedOnly={filters.savedOnly}
        onToggleSavedOnly={handleToggleSavedOnly}
        freshnessDays={filters.freshnessDays}
        onSelectFreshness={handleSelectFreshness}
        filters={filters}
        onFilterChange={handleFilterChange}
        onResetFilters={handleResetFilters}
        onOpenDirectory={() => setIsDirectoryOpen(true)}
        monitoredCount={targetStats?.total_targets}
        syncFreshnessText={syncFreshnessText}
        isSyncing={syncStatus?.is_running}
      />

      {/* Column 2: Central Master Job Stream (MasterJobStream.tsx) */}
      <MasterJobStream
        jobs={displayedJobs}
        totalCount={filters.savedOnly ? displayedJobs.length : totalMatches}
        selectedJob={selectedJob}
        onSelectJob={setSelectedJob}
        isLoading={isLoading}
        isBookmarked={isBookmarked}
        onToggleBookmark={toggleBookmark}
        onOpenInsights={handleOpenInsights}
        onOpenReferral={handleOpenReferral}
        query={filters.searchPrompt}
        onQueryChange={handleQueryChange}
        onSearch={handleSearchSubmit}
        parsedQuery={parsedQuery}
        filters={filters}
        onFilterChange={handleFilterChange}
        onResetFilters={handleResetFilters}
        searchRef={searchRef}
        onOpenDirectory={() => setIsDirectoryOpen(true)}
        monitoredCount={targetStats?.total_targets}
        syncFreshnessText={syncFreshnessText}
      />

      {/* Column 3: Persistent Right-Side Job Inspector (JobInspectorPane.tsx) */}
      <JobInspectorPane
        job={selectedJob}
        isBookmarked={selectedJob ? isBookmarked(selectedJob.id) : false}
        onToggleBookmark={toggleBookmark}
        onClose={() => setSelectedJob(null)}
        onOpenReferral={handleOpenReferral}
      />

      {/* Slide-over Community Insights Drawer */}
      <CommunityInsightsDrawer
        job={insightsJob}
        isOpen={isInsightsOpen}
        onClose={handleCloseInsights}
      />

      {/* Candidate Referral & Lead Capture Modal */}
      <LeadCaptureModal
        job={referralJob}
        isOpen={isReferralModalOpen}
        onClose={() => setIsReferralModalOpen(false)}
      />

      {/* Career Directory Hub Modal */}
      <CareerDirectoryModal
        isOpen={isDirectoryOpen}
        onClose={() => setIsDirectoryOpen(false)}
        onSelectCompany={(companyName) => {
          setFilters((prev) => ({
            ...prev,
            company: companyName,
            searchPrompt: '',
          }));
          setIsDirectoryOpen(false);
        }}
      />
    </div>
  );
}

export default App;
