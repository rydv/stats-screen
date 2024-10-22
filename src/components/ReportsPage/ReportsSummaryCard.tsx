import React, { Component } from 'react';
import './styles/ReportsSummaryCard.css';

interface SummaryData {
  totalReports: number;
  completedToday: number;
  runningNow: number;
  failedToday: number;
  scheduledToday: number;
  averageProcessingTime: string;
}

interface ReportsSummaryCardState {
  summaryData: SummaryData;
  isLoading: boolean;
}

class ReportsSummaryCard extends Component<{}, ReportsSummaryCardState> {
  state: ReportsSummaryCardState = {
    summaryData: {
      totalReports: 50,
      completedToday: 25,
      runningNow: 5,
      failedToday: 3,
      scheduledToday: 17,
      averageProcessingTime: '15 minutes'
    },
    isLoading: false
  };

  componentDidMount() {
    this.fetchSummaryData();
  }

  fetchSummaryData = () => {
    this.setState({ isLoading: true });

    // Commented out API call
    /*
    fetch('/api/reports/summary')
      .then(response => response.json())
      .then(data => {
        this.setState({ summaryData: data, isLoading: false });
      })
      .catch(error => {
        console.error('Error fetching summary data:', error);
        this.setState({ isLoading: false });
      });
    */

    // Simulating API call with setTimeout
    setTimeout(() => {
      this.setState({ isLoading: false });
    }, 1000);
  }

  render() {
    const { summaryData, isLoading } = this.state;

    if (isLoading) {
      return <div className="summary-card loading">Loading summary...</div>;
    }

    return (
      <div className="summary-card">
        <div className="summary-header-container">
          <h2>Reports Summary</h2>
          <div className="average-time">
            <p><strong>Average Processing Time:</strong> <i>{summaryData.averageProcessingTime}</i></p>
          </div>
        </div>
        <div className="summary-grid">
          <div className="summary-item total-reports">
            <h3>Total Reports</h3>
            <p>{summaryData.totalReports}</p>
          </div>
          <div className="summary-item completed-today">
            <h3>Completed Today</h3>
            <p>{summaryData.completedToday}</p>
          </div>
          <div className="summary-item running-now">
            <h3>Running Now</h3>
            <p>{summaryData.runningNow}</p>
          </div>
          <div className="summary-item failed-today">
            <h3>Failed Today</h3>
            <p>{summaryData.failedToday}</p>
          </div>
          <div className="summary-item scheduled-today">
            <h3>Scheduled Today</h3>
            <p>{summaryData.scheduledToday}</p>
          </div>
        </div>
      </div>
    );
  }
}

export default ReportsSummaryCard;