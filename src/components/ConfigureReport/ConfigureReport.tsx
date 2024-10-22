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
  enabled: boolean;
}

class ConfigureReport extends Component<ConfigureReportProps, ConfigureReportState> {
  state: ConfigureReportState = {
    reportName: '',
    instance: '',
    country: '',
    uploadedFile: null,
    enabled: true,
  };

  handleFeatureChange = (name: string, value: string | boolean) => {
    this.setState(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  handleFileUpload = (fileName: string) => {
    this.setState({ uploadedFile: fileName });
  };

  handleToggle = () => {
    this.setState(prevState => ({ enabled: !prevState.enabled }));
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
              enabled: this.state.enabled,
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
        <div className="actions">
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={this.state.enabled}
              onChange={this.handleToggle}
            />
            <span className="slider">
              <span className="toggle-text">{this.state.enabled ? 'Enabled' : 'Disabled'}</span>
            </span>
          </label>
          <button onClick={this.handleValidate}>Validate</button>
          <button onClick={this.handleSubmit}>Submit</button>
        </div>
        <div className="main-content">
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
      </div>
    );
  }
}

export default ConfigureReport;
