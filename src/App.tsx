import React from 'react';
import './App.css';
import FileTable from './components/FileTable/FileTable';
import ConfigureReport from './components/ConfigureReport/ConfigureReport';

function App() {
  return (
    <div className="App">
      <h1>File Table</h1>
      {/* <FileTable /> */}
      <ConfigureReport />
    </div>
  );
}

export default App;
