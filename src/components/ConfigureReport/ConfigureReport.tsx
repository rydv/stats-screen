import React, { Component } from 'react';
import FeaturesForm from './FeaturesForm';
import UploadCard from './UploadCard';
import './ConfigureReport.css';

interface ConfigureReportState {
  reportName: string;
  instance: string;
  country: string;
  uploadedFile: string | null;
}

class ConfigureReport extends Component<{}, ConfigureReportState> {
  state: ConfigureReportState = {
    reportName: '',
    instance: '',
    country: '',
    uploadedFile: null,
  };

  handleFeatureChange = (name: string, value: string) => {
    this.setState({ [name]: value } as Pick<ConfigureReportState, keyof ConfigureReportState>);
  };

  handleFileUpload = (fileName: string) => {
    this.setState({ uploadedFile: fileName });
  };

  handleValidate = () => {
    console.log('Validating...');
  };

  handleSubmit = () => {
    console.log('Submitting...');
  };

  render() {
    return (
      <div className="configure-report">
        <h1>Configure Report</h1>
        <div className="main-content" style={{ display: 'flex', flexDirection: 'row' }}>
          <FeaturesForm
            reportName={this.state.reportName}
            instance={this.state.instance}
            country={this.state.country}
            onChange={this.handleFeatureChange}
          />
          <UploadCard
            uploadedFile={this.state.uploadedFile}
            onFileUpload={this.handleFileUpload}
          />
        </div>
        <div className="actions">
          <button onClick={this.handleValidate}>Validate</button>
          <button onClick={this.handleSubmit}>Submit</button>
        </div>
      </div>
    );
  }
}

export default ConfigureReport;