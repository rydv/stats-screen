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

class FileDetailsPopup extends React.Component<Props> {
  getProgressColor(step: number): string {
    const { progressStatus } = this.props.file;
    const stepOrder = ['inqueue', 'initiated', 'validated', 'processing', 'reportGenerated'];
    const currentStepIndex = stepOrder.indexOf(progressStatus);

    if (step < currentStepIndex) {
      return 'blue';
    } else if (step === currentStepIndex) {
      switch (progressStatus) {
        case 'processing':
          return 'yellow blink';
        case 'validationFailed':
        case 'processingFailed':
          return 'red';
        default:
          return 'blue';
      }
    }
    return 'blank';
  }

  getStatusLabel(step: number): string {
    const labels = ['In Queue', 'Initiated', 'Validated', 'Processing', 'Completed'];
    return labels[step];
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
            <div className={`progress-line ${this.getProgressColor(4)}`}></div>
            {[0, 1, 2, 3, 4].map((step) => (
              <div key={step} className="progress-step">
                <div className={`progress-dot ${this.getProgressColor(step)}`}></div>
                <div className="progress-label">{this.getStatusLabel(step)}</div>
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
