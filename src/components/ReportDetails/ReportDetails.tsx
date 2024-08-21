import React, { Component } from 'react';

interface ReportDetailsProps {
  output: {
    report_id: string;
    record_data: {
      instance: string;
      [key: string]: string;
    };
  };
}

class ReportDetails extends Component<ReportDetailsProps> {
  componentDidMount() {
    console.log('Report Details Output:', this.props.output);
  }

  render() {
    return (
      <div className="report-details">
        <h1>Report Details</h1>
        <p>Report ID: {this.props.output.report_id}</p>
      </div>
    );
  }
}

export default ReportDetails;
