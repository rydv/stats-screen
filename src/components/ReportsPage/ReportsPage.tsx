import React, { Component } from 'react';
import FilterForm from './FilterForm';
import ConfiguredReportsTable from './ConfiguredReportsTable';
import './styles/ReportsPage.css';

interface IReport {
  reportName: string;
  instance: string;
  country: string;
  lastUpdatedDate: string;
  updatedBy: string;
  lastRunDate: string;
  lastRunStatus: string;
}

interface IReportsPageProps {
  onConfigureReport: () => void;
}

interface IReportsPageState {
  reports: IReport[];
  filteredReports: IReport[];
  instanceFilter: string;
  countryFilter: string;
  searchTerm: string;
  isLoading: boolean;
}

class ReportsPage extends Component<IReportsPageProps, IReportsPageState> {
  state: IReportsPageState = {
    reports: [],
    filteredReports: [],
    instanceFilter: '',
    countryFilter: '',
    searchTerm: '',
    isLoading: true,
  };

  async componentDidMount() {
    await new Promise(resolve => setTimeout(resolve, 2000));
    const dummyReports: IReport[] = [
      {
        reportName: "Sales Report",
        instance: "Instance 1",
        country: "USA",
        lastUpdatedDate: "2023-05-01",
        updatedBy: "John Doe",
        lastRunDate: "2023-05-10",
        lastRunStatus: "Completed"
      },
      {
        reportName: "Inventory Report",
        instance: "Instance 2",
        country: "Canada",
        lastUpdatedDate: "2023-05-05",
        updatedBy: "Jane Smith",
        lastRunDate: "2023-05-12",
        lastRunStatus: "Running"
      },
      {
        reportName: "Customer Satisfaction Survey",
        instance: "Instance 1",
        country: "UK",
        lastUpdatedDate: "2023-04-28",
        updatedBy: "Mike Johnson",
        lastRunDate: "2023-05-08",
        lastRunStatus: "Failed"
      },
      {
        reportName: "Monthly Financial Report",
        instance: "Instance 3",
        country: "Germany",
        lastUpdatedDate: "2023-05-15",
        updatedBy: "Anna Schmidt",
        lastRunDate: "2023-05-20",
        lastRunStatus: "Scheduled"
      },
      // ... (add more dummy reports here)
    ];
    this.setState({ 
      reports: dummyReports, 
      filteredReports: dummyReports,
      isLoading: false 
    });
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
    const { filteredReports, instanceFilter, countryFilter, searchTerm, reports, isLoading } = this.state;

    const instances = Array.from(new Set(reports.map(report => report.instance)));
    const countries = Array.from(new Set(reports.map(report => report.country)));

    return (
      <div className="landing-page">
        <div className="header-container">
          <h1>Configured Reports</h1>
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
        <ConfiguredReportsTable reports={filteredReports} isLoading={isLoading} />
      </div>
    );
  }
}

export default ReportsPage;
