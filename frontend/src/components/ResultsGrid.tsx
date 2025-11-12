import React from 'react';
import './ResultsGrid.css';
import ProfileCard from './ProfileCard';
import type { Profile } from '../types';

interface ResultsGridProps {
  results: Profile[];
  loading: boolean;
  onProfileClick: (profile: Profile) => void;
}

const ResultsGrid: React.FC<ResultsGridProps> = ({ results, loading, onProfileClick }) => {
  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner-large"></div>
        <p>Searching...</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        <p>No results found. Try a different search query.</p>
      </div>
    );
  }

  return (
    <div className="results-grid">
      <div className="results-header">
        <h2>Found {results.length} {results.length === 1 ? 'profile' : 'profiles'}</h2>
      </div>
      <div className="grid-container">
        {results.map((profile, index) => (
          <ProfileCard
            key={`${profile.name}-${index}`}
            profile={profile}
            onClick={() => onProfileClick(profile)}
          />
        ))}
      </div>
    </div>
  );
};

export default ResultsGrid;

