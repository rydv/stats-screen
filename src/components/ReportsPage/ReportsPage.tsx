import React, { Component } from 'react';
import FilterForm from './FilterForm';
import ConfiguredReportsTable from './ConfiguredReportsTable';
import './styles/ReportsPage.css';

interface IReportsPageProps {
  onConfigureReport: () => void;
}

interface IReport {
  reportName: string;
  instance: string;
  country: string;
  lastUpdatedDate: string;
  updatedBy: string;
  lastRunDate: string;
}

interface IReportsPageState {
  reports: IReport[];
  filteredReports: IReport[];
  instanceFilter: string;
  countryFilter: string;
  searchTerm: string;
}

class ReportsPage extends Component<IReportsPageProps, IReportsPageState> {
  state: IReportsPageState = {
    reports: [], // This will be populated with actual data
    filteredReports: [],
    instanceFilter: '',
    countryFilter: '',
    searchTerm: '',
  };

  componentDidMount() {
    // Fetch reports data and update state
    // For now, we'll use dummy data
    const dummyReports: IReport[] = [
      {
        reportName: "Sales Report",
        instance: "Instance 1",
        country: "USA",
        lastUpdatedDate: "2023-05-01",
        updatedBy: "John Doe",
        lastRunDate: "2023-05-10"
      },
      {
        reportName: "Inventory Report",
        instance: "Instance 2",
        country: "UK",
        lastUpdatedDate: "2023-04-28",
        updatedBy: "Jane Smith",
        lastRunDate: "2023-05-09"
      },
      {
        reportName: "Financial Report",
        instance: "Instance 1",
        country: "Germany",
        lastUpdatedDate: "2023-05-03",
        updatedBy: "Alice Johnson",
        lastRunDate: "2023-05-11"
      },
      {
        reportName: "Customer Satisfaction Report",
        instance: "Instance 3",
        country: "France",
        lastUpdatedDate: "2023-04-30",
        updatedBy: "Bob Williams",
        lastRunDate: "2023-05-08"
      },
      {
        reportName: "Marketing Campaign Report",
        instance: "Instance 2",
        country: "Japan",
        lastUpdatedDate: "2023-05-02",
        updatedBy: "Charlie Brown",
        lastRunDate: "2023-05-12"
      }
    ];
    this.setState({ reports: dummyReports, filteredReports: dummyReports });
  }

  handleFilterChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = event.target;
    if (name === 'instanceFilter' || name === 'countryFilter') {
      this.setState({ [name]: value } as Pick<IReportsPageState, 'instanceFilter' | 'countryFilter'>, this.filterReports);
    }
  };
  
  clearFilters = () => {
    this.setState({
      instanceFilter: '',
      countryFilter: '',
      searchTerm: '',
    }, this.filterReports);
  };

  handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({ searchTerm: event.target.value }, this.filterReports);
  };

  filterReports = () => {
    const { reports, instanceFilter, countryFilter, searchTerm } = this.state;
    let filtered = reports;

    if (instanceFilter) {
      filtered = filtered.filter(report => report.instance === instanceFilter);
    }

    if (countryFilter) {
      filtered = filtered.filter(report => report.country === countryFilter);
    }

    if (searchTerm) {
      filtered = filtered.filter(report => 
        report.reportName.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    this.setState({ filteredReports: filtered });
  };

  render() {
    const { filteredReports, instanceFilter, countryFilter, searchTerm, reports } = this.state;

    const instances = Array.from(new Set(reports.map(report => report.instance)));
    const countries = Array.from(new Set(reports.map(report => report.country)));

    return (
      <div className="landing-page">
        <div className="header-container">
          <h2>Configured Reports</h2>
          <button className="configure-report-button" onClick={this.props.onConfigureReport}>+ Configure Report</button>
        </div>
        <FilterForm 
          instanceFilter={instanceFilter}
          countryFilter={countryFilter}
          searchTerm={searchTerm}
          onFilterChange={this.handleFilterChange}
          onSearchChange={this.handleSearchChange}
          onClearFilters={this.clearFilters}
          instances={instances}
          countries={countries}
        />
        <ConfiguredReportsTable reports={filteredReports} />
      </div>
    );
  }
}

export default ReportsPage;
