import React, { Component } from 'react';
import './App.css';
import ConfigureReport from './components/ConfigureReport/ConfigureReport';
import ReportDetails from './components/ReportDetails/ReportDetails';
import ReportsPage from './components/ReportsPage/ReportsPage';

interface AppState {
  currentScreen: 'reports' | 'configure' | 'details';
  reportOutput: any | null;
  notification: { message: string; type: 'loading' | 'success' | 'error' } | null;
}

class App extends Component<{}, AppState> {
  state: AppState = {
    currentScreen: 'reports',
    reportOutput: null,
    notification: null,
  };

  notificationTimeout: NodeJS.Timeout | null = null;

  handleReportSubmit = (output: any) => {
    this.setState({
      currentScreen: 'details',
      reportOutput: output,
    });
  };

  setNotification = (message: string, type: 'loading' | 'success' | 'error') => {
    this.setState({ notification: { message, type } });

    if (this.notificationTimeout) {
      clearTimeout(this.notificationTimeout);
    }

    if (type !== 'loading') {
      this.notificationTimeout = setTimeout(() => {
        this.setState({ notification: null });
      }, 5000);
    }
  };

  clearNotification = () => {
    this.setState({ notification: null });
    if (this.notificationTimeout) {
      clearTimeout(this.notificationTimeout);
    }
  };

  changeScreen = (screen: 'reports' | 'configure' | 'details') => {
    this.setState({ currentScreen: screen });
  };

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <div className="logo-container">
            <img src="https://placehold.co/200x100?text=Analytics+Logo" alt="Analytics Logo" className="logo" />
            <span className="header-text">STATS SCREEN</span>
          </div>
          <nav className="horizontal-menu">
            <ul>
              <li><a href="#" onClick={() => this.setState({ currentScreen: 'reports' })}>Home</a></li>
              <li><a href="#" onClick={() => this.setState({ currentScreen: 'configure' })}>Configure Report</a></li>
              <li><a href="#">Analytics</a></li>
            </ul>
          </nav>
        </header>
        {this.state.notification && (
          <div className={`notification-bar ${this.state.notification.type}`}>
            {this.state.notification.message}
            {this.state.notification.type === 'loading' ? (
              <div className="loading-animation"></div>
            ) : (
              <span className="close-icon" onClick={this.clearNotification}>×</span>
            )}
          </div>
        )}
        {this.state.currentScreen === 'reports' && <ReportsPage onConfigureReport={() => this.changeScreen('configure')}/>}
        {this.state.currentScreen === 'configure' && (
          <ConfigureReport 
            onSubmitSuccess={this.handleReportSubmit} 
            setNotification={this.setNotification}
          />
        )}
        {this.state.currentScreen === 'details' && (
          <ReportDetails output={this.state.reportOutput} />
        )}
      </div>
    );
  }
}

export default App;
