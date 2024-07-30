import React from 'react';
import './FileDetailsPopup.css';

interface FileData {
  fileName: string;
  startTime: string;
  endTime: string;
  status: string;
  progressStatus: 'inqueue' | 'initiated' | 'validated' | 'validationFailed' | 'processing' | 'processed' | 'processingFailed' | 'reportGenerated';
}

interface RunSummary {
  matches: string;
  matches_count: {
    [key: string]: number;
  };
}

interface Props {
  file: FileData;
  onClose: () => void;
  fileDetails?: {
    run_summary: RunSummary;
  };
}

interface StatusMapping {
  status: FileData['progressStatus'];
  label: string;
  color: string;
}

interface ProgressStep {
  stepName: string;
  statusMappings: StatusMapping[];
}

class FileDetailsPopup extends React.Component<Props> {
  private progressSteps: ProgressStep[] = [
    {
      stepName: "In-queue",
      statusMappings: [{
        status: 'inqueue',
        label: 'In Queue',
        color: 'blue'
      }]
    },
    {
      stepName: "Initiation",
      statusMappings: [{
        status: 'initiated',
        label: 'Initiating',
        color: 'yellow'
      }, {
        status: 'initiated',
        label: 'Initiated',
        color: 'blue'
      }]
    },
    {
      stepName: "Validation",
      statusMappings: [{
        status: 'validated',
        label: 'Validating',
        color: 'yellow'
      }, {
        status: 'validated',
        label: 'Validation Successful',
        color: 'blue'
      }, {
        status: 'validationFailed',
        label: 'Validation Failed',
        color: 'red'
      }]
    },
    {
      stepName: "Processing",
      statusMappings: [{
        status: 'processing',
        label: 'Processing',
        color: 'yellow'
      }, {
        status: 'processed',
        label: 'Processing Complete',
        color: 'blue'
      }, {
        status: 'processingFailed',
        label: 'Processing Failed',
        color: 'red'
      }]
    },
    {
      stepName: "Report Generation",
      statusMappings: [{
        status: 'reportGenerated',
        label: 'Generating Report',
        color: 'yellow'
      }, {
        status: 'reportGenerated',
        label: 'Report Generated',
        color: 'blue'
      }]
    }
  ];

  getProgressColor(step: number): string {
    const { progressStatus } = this.props.file;
    const currentStep = this.progressSteps.findIndex(s =>
      s.statusMappings.some(mapping => mapping.status === progressStatus)
    );

    if (step < currentStep) {
      return 'blue';
    } else if (step === currentStep) {
      const statusMapping = this.progressSteps[step].statusMappings.find(
        mapping => mapping.status === progressStatus
      );
      return statusMapping ? statusMapping.color : 'blank';
    }
    return 'blank';
  }

  getStatusLabel(step: number): string {
    const { progressStatus } = this.props.file;
    const statusMapping = this.progressSteps[step].statusMappings.find(
      mapping => mapping.status === progressStatus
    );
    return statusMapping ? statusMapping.label : this.progressSteps[step].stepName;
  }

  renderRunSummary() {
    const { fileDetails } = this.props;
    if (!fileDetails || !fileDetails.run_summary) return null;

    const { matches, matches_count } = fileDetails.run_summary;

    return (
      <div className="run-summary">
        <h3>Run Summary</h3>
        <div className="matches">
          <strong>Matches:</strong> {matches}
        </div>
        <div className="matches-count">
          <h4>Matches Count:</h4>
          <table>
            <tbody>
              {Object.entries(matches_count).map(([rule, count]) => (
                <tr key={rule}>
                  <td>{rule}</td>
                  <td>{count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  render() {
    const { file, onClose } = this.props;

    return (
      <div className="file-details-overlay">
        <div className="file-details-popup">
          <div className="header-bar">
            <h2>{file.fileName}</h2>
            <div className="header-icons">
              <button className="icon-button" onClick={() => console.log('Download report')}>
                📥
              </button>
              <button className="icon-button" onClick={onClose}>
                ✖️
              </button>
            </div>
          </div>
          <div className="progress-bar">
            <div className={`progress-line ${this.getProgressColor(this.progressSteps.length - 1)}`}></div>
            {this.progressSteps.map((step, index) => (
              <div key={index} className="progress-step">
                <div className={`progress-dot ${this.getProgressColor(index)}`}></div>
                <div className="progress-label">{this.getStatusLabel(index)}</div>
              </div>
            ))}
          </div>
          <div className="content-area">
            <div className="file-info">
              <h3>File Information</h3>
              <p><strong>File Name:</strong> {file.fileName}</p>
              <p><strong>Start Time:</strong> {file.startTime}</p>
              <p><strong>End Time:</strong> {file.endTime}</p>
              <p><strong>Status:</strong> {file.status}</p>
            </div>
            {this.renderRunSummary()}
          </div>
        </div>
      </div>
    );
  }
}

export default FileDetailsPopup;
