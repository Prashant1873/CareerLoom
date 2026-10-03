import React, { useRef, useEffect } from 'react';
import { Search, Sparkles, X, CornerDownLeft, Loader2 } from 'lucide-react';
import type { ParsedQuery } from '../types/job';

interface SearchBarProps {
  query: string;
  onQueryChange: (query: string) => void;
  onSearch: (query: string) => void;
  isLoading: boolean;
  parsedQuery: ParsedQuery | null;
}

const EXAMPLE_PROMPTS = [
  'junior product manager in Europe or remote',
  'machine learning new grad',
  'quant researcher python',
  'entry level software engineer remote',
];

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  onQueryChange,
  onSearch,
  isLoading,
  parsedQuery,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  // Keyboard shortcut: '/' to focus, 'Escape' to blur
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        e.key === '/' &&
        document.activeElement !== inputRef.current &&
        !['input', 'textarea'].includes((document.activeElement?.tagName || '').toLowerCase())
      ) {
        e.preventDefault();
        inputRef.current?.focus();
      } else if (e.key === 'Escape' && document.activeElement === inputRef.current) {
        inputRef.current?.blur();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  const handleClear = () => {
    onQueryChange('');
    onSearch('');
    inputRef.current?.focus();
  };

  const handlePromptClick = (prompt: string) => {
    onQueryChange(prompt);
    onSearch(prompt);
  };

  const hasParsedAttrs =
    parsedQuery &&
    (parsedQuery.category ||
      parsedQuery.seniority ||
      parsedQuery.country ||
      parsedQuery.is_remote !== null ||
      parsedQuery.posted_within_days);

  return (
    <div className="search-section">
      <form className="search-bar-wrapper" onSubmit={handleSubmit}>
        <div className="search-icon-wrapper">
          {isLoading ? (
            <Loader2 className="search-icon spin" size={20} />
          ) : (
            <Search className="search-icon" size={20} />
          )}
        </div>

        <input
          ref={inputRef}
          type="text"
          className="search-input"
          placeholder="Ask in natural language (e.g. 'entry level product management in Europe or remote')..."
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          aria-label="Search jobs with natural language"
        />

        <div className="search-actions">
          {query && (
            <button
              type="button"
              className="clear-query-btn"
              onClick={handleClear}
              title="Clear search"
              aria-label="Clear search text"
            >
              <X size={16} />
            </button>
          )}
          <button
            type="submit"
            className="search-submit-btn"
            disabled={isLoading}
            title="Search"
          >
            <span>Search</span>
            <CornerDownLeft size={14} className="key-icon" />
          </button>
        </div>
      </form>

      {/* Real-time NLP parsing readout badge */}
      {hasParsedAttrs && parsedQuery && (
        <div className="nlp-feedback-bar animate-fade-in">
          <div className="nlp-badge">
            <Sparkles size={14} className="nlp-sparkle" />
            <span className="nlp-provider">
              {parsedQuery.model_provider === 'fallback' ? 'Heuristic Rule Parser' : 'AI Model'}:
            </span>
          </div>
          <div className="nlp-tags">
            {parsedQuery.category && (
              <span className="nlp-tag category">Category: {parsedQuery.category}</span>
            )}
            {parsedQuery.seniority && (
              <span className="nlp-tag seniority">Level: {parsedQuery.seniority}</span>
            )}
            {parsedQuery.country && (
              <span className="nlp-tag location">Geo: {parsedQuery.country}</span>
            )}
            {parsedQuery.is_remote && (
              <span className="nlp-tag remote">Remote Only</span>
            )}
            {parsedQuery.posted_within_days && (
              <span className="nlp-tag freshness">Within {parsedQuery.posted_within_days}d</span>
            )}
          </div>
        </div>
      )}

      {/* Suggested prompts */}
      <div className="search-suggestions">
        <span className="suggestions-label">Try asking:</span>
        <div className="suggestions-list">
          {EXAMPLE_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="suggestion-chip"
              onClick={() => handlePromptClick(prompt)}
            >
              "{prompt}"
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
