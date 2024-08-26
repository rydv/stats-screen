import React, { Component } from 'react';
import './styles/ConfiguredReportsTable.css';

interface IReport {
  reportName: string;
  instance: string;
  country: string;
  lastUpdatedDate: string;
  updatedBy: string;
  lastRunDate: string;
}

interface IConfiguredReportsTableProps {
  reports: IReport[];
  isLoading: boolean;
}

class ConfiguredReportsTable extends Component<IConfiguredReportsTableProps> {
  render() {
    const { reports, isLoading } = this.props;

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
          {isLoading ? (
            <tr>
              <td colSpan={6} className="fetching">Fetching...</td>
            </tr>
          ) : reports.length === 0 ? (
            <tr>
              <td colSpan={6} className="no-reports">No reports found</td>
            </tr>
          ) : (
            reports.map((report, index) => (
              <tr key={index}>
                <td>{report.reportName}</td>
                <td>{report.instance}</td>
                <td>{report.country}</td>
                <td>{report.lastUpdatedDate}</td>
                <td>{report.updatedBy}</td>
                <td>{report.lastRunDate}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    );
  }
}

export default ConfiguredReportsTable;
