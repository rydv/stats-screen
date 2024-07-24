import React from 'react';
import './FileTable.css';
import FileDetailsPopup from '../FileDetailsPopup/FileDetailsPopup';

interface FileData {
  fileName: string;
  startTime: string;
  endTime: string;
  status: string;
}

interface State {
  selectedFile: FileData | null;
}

class FileTable extends React.Component<{}, State> {
  private mockData: FileData[] = [
    { fileName: 'file1.txt', startTime: '2023-05-01 10:00', endTime: '2023-05-01 11:00', status: 'Completed' },
    { fileName: 'file2.txt', startTime: '2023-05-02 09:00', endTime: '2023-05-02 09:30', status: 'In Progress' },
    { fileName: 'file3.txt', startTime: '2023-05-03 14:00', endTime: '2023-05-03 15:00', status: 'Failed' },
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
          />
        )}
      </div>
    );
  }
}

export default FileTable;
