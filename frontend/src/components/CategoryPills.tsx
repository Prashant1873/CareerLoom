import React from 'react';
import type { Category, DiscoveryTrack } from '../types/job';
import { Layers } from 'lucide-react';

interface CategoryPillsProps {
  categories: Category[];
  tracks: DiscoveryTrack[];
  selectedCategory: string;
  onSelectCategory: (categoryId: string) => void;
  onSelectTrack: (track: DiscoveryTrack) => void;
}

export const CategoryPills: React.FC<CategoryPillsProps> = ({
  categories,
  tracks,
  selectedCategory,
  onSelectCategory,
  onSelectTrack,
}) => {
  return (
    <div className="category-section">
      <div className="category-scroll-container">
        <button
          type="button"
          className={`category-pill ${selectedCategory === '' ? 'active' : ''}`}
          onClick={() => onSelectCategory('')}
        >
          <Layers size={14} className="pill-icon" />
          <span>All Categories</span>
        </button>

        {categories.map((cat) => {
          const isActive = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              type="button"
              className={`category-pill ${isActive ? 'active' : ''}`}
              onClick={() => onSelectCategory(cat.id)}
            >
              <span>{cat.label}</span>
            </button>
          );
        })}
      </div>

      {/* Featured quick tracks for exploratory search */}
      {tracks.length > 0 && (
        <div className="tracks-scroll-container">
          <span className="tracks-label">Popular Tracks:</span>
          {tracks.slice(0, 10).map((trk) => (
            <button
              key={trk.track}
              type="button"
              className="track-chip"
              onClick={() => onSelectTrack(trk)}
              title={`Explore ${trk.track}`}
            >
              {trk.track}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
