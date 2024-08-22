import React, { Component } from 'react';
import './styles/FilterForm.css';

interface IFilterFormProps {
  instanceFilter: string;
  countryFilter: string;
  searchTerm: string;
  onFilterChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
  onSearchChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onClearFilters: () => void;
  instances: string[];
  countries: string[];
}

class FilterForm extends Component<IFilterFormProps> {
  render() {
    const { instanceFilter, countryFilter, searchTerm, onFilterChange, onSearchChange, onClearFilters, instances, countries } = this.props;

    return (
      <div className="filter-form">
        <div className="filter-row">
          <div className="filter-group">
            <label htmlFor="instanceFilter">Instance</label>
            <select name="instanceFilter" value={instanceFilter} onChange={onFilterChange}>
              <option value="">All Instances</option>
              {instances.map((instance, index) => (
                <option key={index} value={instance}>{instance}</option>
              ))}
            </select>
          </div>
          <div className="filter-group">
            <label htmlFor="countryFilter">Country</label>
            <select name="countryFilter" value={countryFilter} onChange={onFilterChange}>
              <option value="">All Countries</option>
              {countries.map((country, index) => (
                <option key={index} value={country}>{country}</option>
              ))}
            </select>
          </div>
          <button className="clear-filters" onClick={onClearFilters}>Clear</button>
        </div>
        <div className="search-row">
          <input 
            type="text" 
            placeholder="Search report name" 
            value={searchTerm} 
            onChange={onSearchChange}
          />
        </div>
      </div>
    );
  }
}

export default FilterForm;
