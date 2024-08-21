import React, { Component } from 'react';
import FeaturesForm from '../ConfigureReport/FeaturesForm';
import UploadCard from '../ConfigureReport/UploadCard';
import ProcessingStatus from './ProcessingStatus';
import RuleSheetVersion from './RuleSheetVersion';
import './styles/ReportDetails.css';

interface ReportDetailsProps {
  output: {
    report_id: string;
    record_data: {
      instance: string;
      country: string;
      reportName: string;
      uploadedFile: string | null;
    };
  };
}

class ReportDetails extends Component<ReportDetailsProps> {
  handleFileUpload = (fileName: string) => {
    console.log('New file uploaded:', fileName);
    // Here you would typically update the backend with the new file
  };

  render() {
    const { record_data } = this.props.output;

    // Mock data for ProcessingStatus component
    const processingStatusData = {
      lastProcessingDate: '2023-05-01',
      processStartTime: '08:00:00',
      processEndTime: '08:15:30',
      totalTimeTaken: '15m 30s',
      status: 'Completed',
      fileDetails: {
        // Add mock file details here
      }
    };

    // Mock data for RuleSheetVersion component
    const ruleSheetVersionData = {
      currentVersion: {
        uploadedDate: '2023-05-01',
        numberOfRules: 100,
        updatedBy: 'John Doe',
        downloadUrl: '#'
      },
      previousVersion: {
        uploadedDate: '2023-04-15',
        numberOfRules: 95,
        updatedBy: 'Jane Smith',
        downloadUrl: '#'
      }
    };

    return (
      <div className="report-details">
        <h1>Report Details</h1>
        <p className="report-note">Note: Report tag information is read-only. You may update the associated file if needed.</p>
        <p>Report ID: {this.props.output.report_id}</p>
        <div className="main-content" style={{ display: 'flex', flexDirection: 'row' }}>
          <FeaturesForm
            reportName={record_data.reportName}
            instance={record_data.instance}
            country={record_data.country}
            onChange={() => {}} // No-op function since it's disabled
            disabled={true}
          />
          <UploadCard
            uploadedFile={record_data.uploadedFile}
            onFileUpload={this.handleFileUpload}
          />
        </div>
        <ProcessingStatus {...processingStatusData} />
        <RuleSheetVersion
          currentVersion={ruleSheetVersionData.currentVersion}
          previousVersion={ruleSheetVersionData.previousVersion}
        />
      </div>
    );
  }
}

export default ReportDetails;
