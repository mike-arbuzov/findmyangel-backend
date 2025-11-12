import React, { useState } from 'react';
import './FilterPanel.css';
import type { SearchFilters } from '../types';

interface FilterPanelProps {
  filters: SearchFilters;
  maxResults: number;
  onFilterChange: (filters: SearchFilters) => void;
  onMaxResultsChange: (max: number) => void;
  onApply: () => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  maxResults,
  onFilterChange,
  onMaxResultsChange,
  onApply
}) => {
  const [localFilters, setLocalFilters] = useState<SearchFilters>(filters);
  const [localMaxResults, setLocalMaxResults] = useState<number>(maxResults);

  const handleFilterUpdate = (key: keyof SearchFilters, value: string | boolean | null | string[]): void => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
  };

  const handleArrayFilterUpdate = (key: keyof SearchFilters, value: string, checked: boolean): void => {
    const currentArray = (localFilters[key] as string[]) || [];
    const newArray = checked
      ? [...currentArray, value]
      : currentArray.filter(item => item !== value);
    handleFilterUpdate(key, newArray);
  };

  const handleApply = (): void => {
    onFilterChange(localFilters);
    onMaxResultsChange(localMaxResults);
    onApply();
  };

  const handleReset = (): void => {
    const resetFilters: SearchFilters = {
      is_investor: null,
      investment_role: '',
      location: '',
      sectors_of_interest: [],
      investment_stage: []
    };
    setLocalFilters(resetFilters);
    setLocalMaxResults(10);
    onFilterChange(resetFilters);
    onMaxResultsChange(10);
  };

  const commonSectors = ['fintech', 'ai', 'healthtech', 'edtech', 'saas', 'e-commerce', 'blockchain', 'biotech'];
  const commonStages = ['pre-seed', 'seed', 'series a', 'series b', 'series c', 'growth'];

  return (
    <div className="filter-panel">
      <div className="filter-section">
        <h3>Filters</h3>
        
        <div className="filter-group">
          <label>Investor Status</label>
          <div className="radio-group">
            <label>
              <input
                type="radio"
                name="is_investor"
                checked={localFilters.is_investor === true}
                onChange={() => handleFilterUpdate('is_investor', true)}
              />
              Investors Only
            </label>
            <label>
              <input
                type="radio"
                name="is_investor"
                checked={localFilters.is_investor === false}
                onChange={() => handleFilterUpdate('is_investor', false)}
              />
              Non-Investors
            </label>
            <label>
              <input
                type="radio"
                name="is_investor"
                checked={localFilters.is_investor === null}
                onChange={() => handleFilterUpdate('is_investor', null)}
              />
              All
            </label>
          </div>
        </div>

        <div className="filter-group">
          <label htmlFor="investment_role">Investment Role</label>
          <input
            id="investment_role"
            type="text"
            value={localFilters.investment_role}
            onChange={(e) => handleFilterUpdate('investment_role', e.target.value)}
            placeholder="e.g., Angel Investor, VC Partner"
          />
        </div>

        <div className="filter-group">
          <label htmlFor="location">Location</label>
          <input
            id="location"
            type="text"
            value={localFilters.location}
            onChange={(e) => handleFilterUpdate('location', e.target.value)}
            placeholder="e.g., San Francisco, Estonia"
          />
        </div>

        <div className="filter-group">
          <label>Sectors of Interest</label>
          <div className="checkbox-group">
            {commonSectors.map(sector => (
              <label key={sector}>
                <input
                  type="checkbox"
                  checked={localFilters.sectors_of_interest.includes(sector)}
                  onChange={(e) => handleArrayFilterUpdate('sectors_of_interest', sector, e.target.checked)}
                />
                {sector}
              </label>
            ))}
          </div>
        </div>

        <div className="filter-group">
          <label>Investment Stage</label>
          <div className="checkbox-group">
            {commonStages.map(stage => (
              <label key={stage}>
                <input
                  type="checkbox"
                  checked={localFilters.investment_stage.includes(stage)}
                  onChange={(e) => handleArrayFilterUpdate('investment_stage', stage, e.target.checked)}
                />
                {stage}
              </label>
            ))}
          </div>
        </div>

        <div className="filter-group">
          <label htmlFor="max_results">Max Results</label>
          <input
            id="max_results"
            type="number"
            min="1"
            max="100"
            value={localMaxResults}
            onChange={(e) => setLocalMaxResults(parseInt(e.target.value) || 10)}
          />
        </div>
      </div>

      <div className="filter-actions">
        <button className="apply-button" onClick={handleApply}>
          Apply Filters
        </button>
        <button className="reset-button" onClick={handleReset}>
          Reset
        </button>
      </div>
    </div>
  );
};

export default FilterPanel;

