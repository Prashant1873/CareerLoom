import { useEffect } from 'react';
import type { JobItem } from '../types/job';

interface KeyboardNavOptions {
  jobs: JobItem[];
  selectedJob: JobItem | null;
  onSelectJob: (job: JobItem) => void;
  onToggleBookmark: (jobId: string) => void;
  onFocusSearch?: () => void;
}

export function useKeyboardNav({
  jobs,
  selectedJob,
  onSelectJob,
  onToggleBookmark,
  onFocusSearch,
}: KeyboardNavOptions) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is currently typing in an input, textarea, or select
      const activeElement = document.activeElement;
      const isInput =
        activeElement &&
        (activeElement.tagName === 'INPUT' ||
          activeElement.tagName === 'TEXTAREA' ||
          activeElement.tagName === 'SELECT');

      // Allow '/' to focus search from anywhere if not in an input
      if (e.key === '/' && !isInput && onFocusSearch) {
        e.preventDefault();
        onFocusSearch();
        return;
      }

      if (isInput) {
        if (e.key === 'Escape') {
          (activeElement as HTMLElement).blur();
        }
        return;
      }

      if (jobs.length === 0) return;

      const currentIndex = selectedJob ? jobs.findIndex((j) => j.id === selectedJob.id) : -1;

      // 'J' or 'ArrowDown' -> Next Job
      if (e.key === 'j' || e.key === 'ArrowDown') {
        e.preventDefault();
        const nextIndex = currentIndex < jobs.length - 1 ? currentIndex + 1 : 0;
        onSelectJob(jobs[nextIndex]);
      }

      // 'K' or 'ArrowUp' -> Previous Job
      else if (e.key === 'k' || e.key === 'ArrowUp') {
        e.preventDefault();
        const prevIndex = currentIndex > 0 ? currentIndex - 1 : jobs.length - 1;
        onSelectJob(jobs[prevIndex]);
      }

      // 'S' -> Toggle Bookmark
      else if (e.key === 's' || e.key === 'S') {
        if (selectedJob) {
          e.preventDefault();
          onToggleBookmark(selectedJob.id);
        }
      }

      // 'Enter' -> Open official apply URL
      else if (e.key === 'Enter') {
        if (selectedJob && selectedJob.apply_url) {
          e.preventDefault();
          window.open(selectedJob.apply_url, '_blank', 'noopener,noreferrer');
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [jobs, selectedJob, onSelectJob, onToggleBookmark, onFocusSearch]);
}
