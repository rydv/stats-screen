import React, { Component } from 'react';
import './styles/ConfiguredReportsTable.css';

interface Report {
  reportName: string;
  instance: string;
  country: string;
  lastUpdatedDate: string;
  updatedBy: string;
  lastRunDate: string;
}

interface ConfiguredReportsTableProps {
  reports: Report[];
}

class ConfiguredReportsTable extends Component<ConfiguredReportsTableProps> {
  render() {
    const { reports } = this.props;

    return (
      <table className="reports-table">
        <thead>
          <tr>
            <th>Report Name</th>
            <th>Instance</th>
            <th>Country</th>
            <th>Last Updated Date</th>
            <th>Updated By</th>
            <th>Last Run Date</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((report, index) => (
            <tr key={index}>
              <td>{report.reportName}</td>
              <td>{report.instance}</td>
              <td>{report.country}</td>
              <td>{report.lastUpdatedDate}</td>
              <td>{report.updatedBy}</td>
              <td>{report.lastRunDate}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  }
}

export default ConfiguredReportsTable;
