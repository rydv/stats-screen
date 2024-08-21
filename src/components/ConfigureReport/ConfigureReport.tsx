import React, { Component } from 'react';
import FeaturesForm from './FeaturesForm';
import UploadCard from './UploadCard';
import './ConfigureReport.css';

interface ConfigureReportProps {
  onSubmitSuccess: (output: any) => void;
  setNotification: (message: string, type: 'loading' | 'success' | 'error') => void;
}

interface ConfigureReportState {
  reportName: string;
  instance: string;
  country: string;
  uploadedFile: string | null;
}

class ConfigureReport extends Component<ConfigureReportProps, ConfigureReportState> {
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
    this.props.setNotification(`Configuring report: ${this.state.reportName}`, 'loading');

    // Simulate API call
    setTimeout(() => {
      const isSuccess = Math.random() > 0.5; // Simulate success/failure randomly

      if (isSuccess) {
        const mockResponse = {
          status: 'success',
          output: {
            report_id: 'eas245qfgh',
            record_data: {
              instance: this.state.instance,
              country: this.state.country,
              reportName: this.state.reportName,
              uploadedFile: this.state.uploadedFile,
            }
          }
        };

        this.props.setNotification(`Successfully configured report: ${this.state.reportName}`, 'success');
        this.props.onSubmitSuccess(mockResponse.output);
      } else {
        this.props.setNotification('Failed to configure report', 'error');
      }
    }, 2000);
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
