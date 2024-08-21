import React, { Component } from 'react';
import FileDetailsPopup from '../FileDetailsPopup/FileDetailsPopup';
import './styles/ProcessingStatus.css';

interface ProcessingStatusProps {
  lastProcessingDate: string;
  processStartTime: string;
  processEndTime: string;
  totalTimeTaken: string;
  status: string;
  fileDetails: any; // Replace 'any' with the actual type from FileDetailsPopup
}

interface ProcessingStatusState {
  showDetailsPopup: boolean;
  runInfo: {
    lastProcessingDate: string;
    processStartTime: string;
    processEndTime: string;
    totalTimeTaken: string;
    status: string;
  } | null;
  isFetching: boolean;
}

class ProcessingStatus extends Component<ProcessingStatusProps, ProcessingStatusState> {
  state: ProcessingStatusState = {
    showDetailsPopup: false,
    runInfo: null,
    isFetching: true,
  };

  componentDidMount() {
    // Simulating API call to fetch previous run information
    setTimeout(() => {
      // const dummyRunInfo = null; // Simulating empty data return
      // Sample dummyRunInfo case
      const dummyRunInfo = {
        lastProcessingDate: '2023-05-15',
        processStartTime: '10:30:00',
        processEndTime: '11:45:00',
        totalTimeTaken: '1:15:00',
        status: 'Completed'
      };
      this.setState({ runInfo: dummyRunInfo, isFetching: false });
    }, 1000);
  }

  toggleDetailsPopup = () => {
    this.setState(prevState => ({ showDetailsPopup: !prevState.showDetailsPopup }));
  };

  render() {
    const { runInfo, isFetching } = this.state;
    const { fileDetails } = this.props;

    if (isFetching) {
      return (
        <div className="processing-status">
          <h2>Previous Run Status</h2>
          <div className="status-card">
            <div className="status-item">
              <div className="status-value no-info">Information is coming...</div>
            </div>
          </div>
        </div>
      );
    }

    if (!runInfo) {
      return (
        <div className="processing-status">
          <h2>Previous Run Status</h2>
          <div className="status-card">
            <div className="status-item">
              <div className="status-value no-info">No previous run available</div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="processing-status">
        <h2>Previous Run Status</h2>
        <div className="status-card">
          <div className="status-item">
            <div className="status-header">Last Processing Date</div>
            <div className="status-value">{runInfo.lastProcessingDate}</div>
          </div>
          <div className="status-item">
            <div className="status-header">Process Start Time</div>
            <div className="status-value">{runInfo.processStartTime}</div>
          </div>
          <div className="status-item">
            <div className="status-header">Process End Time</div>
            <div className="status-value">{runInfo.processEndTime}</div>
          </div>
          <div className="status-item">
            <div className="status-header">Total Time Taken</div>
            <div className="status-value">{runInfo.totalTimeTaken}</div>
          </div>
          <div className="status-item">
            <div className="status-header">Status</div>
            <div className="status-value">{runInfo.status}</div>
          </div>
          <div className="status-item">
            <div className="status-header">Details</div>
            <div className="status-value">
              <button onClick={this.toggleDetailsPopup}>👁️</button>
            </div>
          </div>
        </div>
        {this.state.showDetailsPopup && (
          <FileDetailsPopup
            file={fileDetails}
            onClose={this.toggleDetailsPopup}
          />
        )}
      </div>
    );
  }
}

export default ProcessingStatus;
