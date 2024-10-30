import React, { Component } from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import CloseIcon from '@mui/icons-material/Close';
import Button from '@mui/material/Button';
import './ValidationPopup.css';

interface ValidationPopupProps {
    file: any;
    formData: {
        reportName: string;
        instance: string;
        country: string;
    };
    onClose: () => void;
    onConfigure: () => void;
}

interface ValidationPopupState {
    status: 'validating' | 'success' | 'error' | 'validation-error';
    errors: string[];
    isLoading: boolean;
}

class ValidationPopup extends Component<ValidationPopupProps, ValidationPopupState> {
    state: ValidationPopupState = {
        status: 'validating',
        errors: [],
        isLoading: true
    };

    componentDidMount() {
        this.validateFile();
    }

    validateFile = async () => {
        try {
            const formData = new FormData();
            formData.append('file', this.props.file);

            const response = await fetch('/api/validate-rule-sheet', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.status) {
                this.setState({ 
                    status: 'success',
                    isLoading: false 
                });
            } else {
                this.setState({ 
                    status: 'validation-error',
                    errors: data.validation_results.errors,
                    isLoading: false 
                });
            }
        } catch (error) {
            this.setState({ 
                status: 'error',
                isLoading: false 
            });
        }
    };

    renderFormElement = (label: string, value: string) => (
        <div className="form-element">
            <div className="form-label">{label}</div>
            <div className="form-value">{value}</div>
        </div>
    );

    renderContent = () => {
        const { status, errors, isLoading } = this.state;
        const { formData } = this.props;

        return (
            <div className="validation-content">
                <div className="form-summary">
                    <h3>Report Configuration</h3>
                    <div className="form-grid">
                        {this.renderFormElement("Report Name", formData.reportName)}
                        {this.renderFormElement("Instance", formData.instance)}
                        {this.renderFormElement("Country", formData.country)}
                        {this.renderFormElement("File", this.props.file.name)}
                    </div>
                </div>

                <div className="validation-status">
                    {isLoading && (
                        <div className="status-indicator">
                            <CircularProgress className="loading-spinner" />
                            <p>Validating rule sheet...</p>
                        </div>
                    )}

                    {!isLoading && status === 'success' && (
                        <div className="status-indicator success">
                            <CheckCircleIcon className="success-icon" />
                            <p>Validation successful!</p>
                        </div>
                    )}

                    {!isLoading && status === 'error' && (
                        <div className="status-indicator error">
                            <ErrorIcon className="error-icon" />
                            <p>Internal server error occurred</p>
                        </div>
                    )}

                    {!isLoading && status === 'validation-error' && (
                        <div className="validation-errors">
                            <ErrorIcon className="error-icon" />
                            <h4>Validation Errors:</h4>
                            <ul>
                                {errors.map((error, index) => (
                                    <li key={index}>{error}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </div>
        );
    };

    render() {
        const { status } = this.state;
        
        return (
            <div className="validation-popup-overlay">
                <div className="validation-popup">
                    <div className="popup-header">
                        <h2>Rule Sheet Validation</h2>
                        <CloseIcon 
                            className="close-button" 
                            onClick={this.props.onClose}
                        />
                    </div>
                    {this.renderContent()}
                    <div className="popup-footer">
                        {status === 'success' && (
                            <Button 
                                variant="contained"
                                color="primary"
                                onClick={this.props.onConfigure}
                                className="configure-button"
                            >
                                Configure Report
                            </Button>
                        )}
                    </div>
                </div>
            </div>
        );
    }
}

export default ValidationPopup;
