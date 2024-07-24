import React from 'react';
import './FileTable.css';
import FileDetailsPopup from '../FileDetailsPopup/FileDetailsPopup';

interface FileData {
  fileName: string;
  startTime: string;
  endTime: string;
  status: string;
  progressStatus: 'inqueue' | 'initiated' | 'validated' | 'validationFailed' | 'processing' | 'processed' | 'processingFailed' | 'reportGenerated';
}

interface State {
  selectedFile: FileData | null;
}

class FileTable extends React.Component<{}, State> {
  private mockData: FileData[] = [
    { fileName: 'file1.txt', startTime: '2023-05-01 10:00', endTime: '2023-05-01 11:00', status: 'Queued', progressStatus: 'inqueue' },
    { fileName: 'file2.txt', startTime: '2023-05-02 09:00', endTime: '2023-05-02 09:30', status: 'Initiated', progressStatus: 'initiated' },
    { fileName: 'file3.txt', startTime: '2023-05-03 14:00', endTime: '2023-05-03 15:00', status: 'Validated', progressStatus: 'validated' },
    { fileName: 'file4.txt', startTime: '2023-05-04 11:00', endTime: '2023-05-04 11:15', status: 'Validation Failed', progressStatus: 'validationFailed' },
    { fileName: 'file5.txt', startTime: '2023-05-05 13:00', endTime: '', status: 'Processing', progressStatus: 'processing' },
    { fileName: 'file6.txt', startTime: '2023-05-06 10:00', endTime: '2023-05-06 10:45', status: 'Processed', progressStatus: 'processed' },
    { fileName: 'file7.txt', startTime: '2023-05-07 09:00', endTime: '2023-05-07 09:30', status: 'Processing Failed', progressStatus: 'processingFailed' },
    { fileName: 'file8.txt', startTime: '2023-05-08 15:00', endTime: '2023-05-08 16:00', status: 'Completed', progressStatus: 'reportGenerated' },
  ];

  state: State = {
    selectedFile: null,
  };

  private handleViewDetails = (file: FileData) => {
    this.setState({ selectedFile: file });
  }

  private handleClosePopup = () => {
    this.setState({ selectedFile: null });
  }

  render() {
    return (
      <div className="file-table-container">
        <table className="file-table">
          <thead>
            <tr>
              <th>File Name</th>
              <th>Started Time</th>
              <th>End Time</th>
              <th>Status</th>
              <th>View Details</th>
            </tr>
          </thead>
          <tbody>
            {this.mockData.map((file, index) => (
              <tr key={index}>
                <td>{file.fileName}</td>
                <td>{file.startTime}</td>
                <td>{file.endTime}</td>
                <td>{file.status}</td>
                <td>
                  <button onClick={() => this.handleViewDetails(file)}>
                    📄
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {this.state.selectedFile && (
          <FileDetailsPopup
            file={this.state.selectedFile}
            onClose={this.handleClosePopup}
            fileDetails={
              this.state.selectedFile.progressStatus === 'reportGenerated'
                ? {
                    run_summary: {
                      matches: "3/5",
                      matches_count: {
                        RUL01: 102,
                        RUL03: 45,
                        RUL04: 32
                      }
                    }
                  }
                : undefined
            }
          />
        )}
      </div>
    );
  }
}

export default FileTable;
