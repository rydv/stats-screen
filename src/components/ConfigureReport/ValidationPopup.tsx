// ValidationPopup.tsx
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
            // Mock sleep for 2 seconds
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Mock successful response
            this.setState({ 
                status: 'success',
                isLoading: false 
            });
        } catch (error) {
            this.setState({ 
                status: 'error',
                isLoading: false 
            });
        }
    };

    renderFormElement = (label: string, value: string, showStatus = false) => (
        <div className="form-element">
            <div className="form-label">{label}</div>
            <div className="form-value-container">
                <div className="form-value text-ellipsis" title={value}>
                    {value}
                </div>
                {showStatus && this.renderStatus()}
            </div>
        </div>
    );

    renderStatus = () => {
        const { status, isLoading } = this.state;
        
        if (isLoading) {
            return <CircularProgress size={20} className="loading-spinner" />;
        }
        
        if (status === 'success') {
            return <CheckCircleIcon className="success-icon-small" />;
        }
        
        return null;
    };

    render() {
        const { status, errors, isLoading } = this.state;
        const { formData } = this.props;
        
        if (!isLoading && status === 'success') {
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
                        
                        <div className="validation-content">
                            <div className="form-summary">
                                <h3>Report Configuration</h3>
                                <div className="form-grid">
                                    {this.renderFormElement("Report Name", formData.reportName)}
                                    {this.renderFormElement("Instance", formData.instance)}
                                    {this.renderFormElement("Country", formData.country)}
                                    {this.renderFormElement("File", this.props.file.name, true)}
                                </div>
                            </div>
                        </div>

                        <div className="popup-footer">
                            <Button 
                                variant="contained"
                                color="primary"
                                onClick={this.props.onConfigure}
                                className="configure-button"
                            >
                                Configure Report
                            </Button>
                        </div>
                    </div>
                </div>
            );
        }

        if (!isLoading && (status === 'error' || status === 'validation-error')) {
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

                            <div className="validation-errors-container">
                                <div className="validation-errors">
                                    <ErrorIcon className="error-icon" />
                                    <h4>{status === 'error' ? 'Internal Server Error' : 'Validation Errors:'}</h4>
                                    {status === 'validation-error' && (
                                        <ul>
                                            {errors.map((error, index) => (
                                                <li key={index}>{error}</li>
                                            ))}
                                        </ul>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="popup-footer">
                            <Button 
                                variant="contained"
                                color="primary"
                                onClick={this.props.onConfigure}
                                className="configure-button"
                                disabled
                            >
                                Configure Report
                            </Button>
                        </div>
                    </div>
                </div>
            );
        }

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
                    
                    <div className="validation-content">
                        <div className="form-summary">
                            <h3>Report Configuration</h3>
                            <div className="form-grid">
                                {this.renderFormElement("Report Name", formData.reportName)}
                                {this.renderFormElement("Instance", formData.instance)}
                                {this.renderFormElement("Country", formData.country)}
                                {this.renderFormElement("File", this.props.file.name, true)}
                            </div>
                        </div>
                    </div>

                    <div className="popup-footer">
                        <Button 
                            variant="contained"
                            color="primary"
                            onClick={this.props.onConfigure}
                            className="configure-button"
                            disabled
                        >
                            Configure Report
                        </Button>
                    </div>
                </div>
            </div>
        );
    }
}

export default ValidationPopup;