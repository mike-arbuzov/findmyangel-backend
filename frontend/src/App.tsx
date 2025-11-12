import { useState } from 'react';
import './App.css';
import SearchBox from './components/SearchBox';
import FilterPanel from './components/FilterPanel';
import ResultsGrid from './components/ResultsGrid';
import ProfileModal from './components/ProfileModal';
import { searchProfiles } from './services/api';
import type { Profile, SearchFilters } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<Profile[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState<boolean>(false);
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null);
  const [filters, setFilters] = useState<SearchFilters>({
    is_investor: null,
    investment_role: '',
    location: '',
    sectors_of_interest: [],
    investment_stage: []
  });
  const [maxResults, setMaxResults] = useState<number>(10);

  const handleSearch = async (searchQuery: string = query): Promise<void> => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Build filters object (only include non-empty values)
      const activeFilters: Partial<SearchFilters> = {};
      if (filters.is_investor !== null) {
        activeFilters.is_investor = filters.is_investor;
      }
      if (filters.investment_role) {
        activeFilters.investment_role = filters.investment_role;
      }
      if (filters.location) {
        activeFilters.location = filters.location;
      }
      if (filters.sectors_of_interest.length > 0) {
        activeFilters.sectors_of_interest = filters.sectors_of_interest;
      }
      if (filters.investment_stage.length > 0) {
        activeFilters.investment_stage = filters.investment_stage;
      }

      const response = await searchProfiles(API_BASE_URL, {
        query: searchQuery,
        max_results: maxResults,
        filters: Object.keys(activeFilters).length > 0 ? (activeFilters as SearchFilters) : null
      });

      setResults(response.results || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search profiles');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters: SearchFilters): void => {
    setFilters(newFilters);
  };

  const handleMaxResultsChange = (newMax: number): void => {
    setMaxResults(newMax);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Find My Angel</h1>
        <p>Search for business angels and investors</p>
      </header>

      <div className="App-container">
        <div className="search-section">
          <SearchBox
            value={query}
            onChange={setQuery}
            onSearch={handleSearch}
            loading={loading}
            showFilters={showFilters}
            onFilterToggle={() => setShowFilters(!showFilters)}
          />

          {showFilters && (
            <FilterPanel
              filters={filters}
              maxResults={maxResults}
              onFilterChange={handleFilterChange}
              onMaxResultsChange={handleMaxResultsChange}
              onApply={() => handleSearch()}
            />
          )}
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <ResultsGrid
          results={results}
          loading={loading}
          onProfileClick={setSelectedProfile}
        />

        {selectedProfile && (
          <ProfileModal
            profile={selectedProfile}
            onClose={() => setSelectedProfile(null)}
          />
        )}
      </div>
    </div>
  );
}

export default App;

