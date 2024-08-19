import React, { Component } from 'react';
import "./UploadCard.css";

interface UploadCardProps {
  uploadedFile: string | null;
  onFileUpload: (fileName: string) => void;
}

class UploadCard extends Component<UploadCardProps> {
  handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      this.props.onFileUpload(file.name);
    }
  };

  render() {
    const { uploadedFile } = this.props;

    return (
      <div className="upload-card">
        <div className="upload-icon" onClick={() => document.getElementById('fileInput')?.click()}>
          📁 Click to upload
        </div>
        <input
          type="file"
          id="fileInput"
          style={{ display: 'none' }}
          onChange={this.handleFileChange}
        />
        <div className="file-name">{uploadedFile || 'No file uploaded'}</div>
        <div className="progress-bar">
          {uploadedFile && (
            <svg width="50" height="50" viewBox="0 0 50 50">
              <circle
                cx="25"
                cy="25"
                r="20"
                fill="none"
                stroke="#4CAF50"
                strokeWidth="5"
                strokeDasharray="125.6"
                strokeDashoffset="0"
              />
            </svg>
          )}
        </div>
      </div>
    );
  }
}

export default UploadCard;
