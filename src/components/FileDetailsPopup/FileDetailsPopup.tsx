import React from 'react';
import './FileDetailsPopup.css';

interface FileData {
  fileName: string;
  startTime: string;
  endTime: string;
  status: string;
}

interface Props {
  file: FileData;
  onClose: () => void;
}

class FileDetailsPopup extends React.Component<Props> {
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
            <div className="progress-line"></div>
            <div className="progress-dot"></div>
            <div className="progress-dot"></div>
            <div className="progress-dot"></div>
            <div className="progress-dot"></div>
          </div>
          <div className="content-area">
            {/* Future components will be added here */}
            <p>File details and additional components will be displayed here.</p>
          </div>
        </div>
      </div>
    );
  }
}

export default FileDetailsPopup;
