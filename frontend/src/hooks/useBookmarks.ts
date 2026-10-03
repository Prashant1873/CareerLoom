import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'careerloom_saved_jobs_v1';

export function useBookmarks() {
  const [savedIds, setSavedIds] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (e) {
      console.error('Failed to read bookmarks from localStorage:', e);
      return [];
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(savedIds));
    } catch (e) {
      console.error('Failed to save bookmarks to localStorage:', e);
    }
  }, [savedIds]);

  const isBookmarked = useCallback(
    (id: string) => savedIds.includes(id),
    [savedIds]
  );

  const toggleBookmark = useCallback((id: string) => {
    setSavedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  }, []);

  return {
    savedIds,
    savedCount: savedIds.length,
    isBookmarked,
    toggleBookmark,
  };
}
