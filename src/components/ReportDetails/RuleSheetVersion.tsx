import React from 'react';
import './styles/RuleSheetVersion.css';

interface FileVersion {
  uploadedDate: string;
  numberOfRules: number;
  updatedBy: string;
  downloadUrl: string;
}

interface RuleSheetVersionProps {
  currentVersion: FileVersion;
  previousVersion: FileVersion | null;
}

const RuleSheetVersion: React.FC<RuleSheetVersionProps> = ({ currentVersion, previousVersion }) => {
  const renderRow = (version: FileVersion, label: string) => (
    <tr>
      <td>{label}</td>
      <td>{version.uploadedDate}</td>
      <td>{version.numberOfRules}</td>
      <td>{version.updatedBy}</td>
      <td>
        <a href={version.downloadUrl} download>
          <span className="download-icon">⬇️</span>
        </a>
      </td>
    </tr>
  );

  return (
    <div className="rule-sheet-version">
      <h2>File Versions</h2>
      <div className="version-card">
        <table>
          <thead>
            <tr>
              <th>Version</th>
              <th>Uploaded Date</th>
              <th>Number of Rules</th>
              <th>Updated By</th>
              <th>Download</th>
            </tr>
          </thead>
          <tbody>
            {renderRow(currentVersion, 'Current')}
            {previousVersion && renderRow(previousVersion, 'Previous')}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RuleSheetVersion;
