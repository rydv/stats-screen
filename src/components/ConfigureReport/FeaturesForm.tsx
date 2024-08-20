import React, { Component } from 'react';
import "./FeaturesForm.css";

interface FeaturesFormProps {
  reportName: string;
  instance: string;
  country: string;
  onChange: (name: string, value: string) => void;
}

const INSTANCES = ['Instance 1', 'Instance 2', 'Instance 3'];
const COUNTRIES = ['USA', 'UK', 'Germany', 'France', 'Japan'];

class FeaturesForm extends Component<FeaturesFormProps> {
  handleInputChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    this.props.onChange(name, value);
  };

  render() {
    const { reportName, instance, country } = this.props;

    return (
      <form className="features-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="reportName">Report Name:</label>
            <input
              type="text"
              id="reportName"
              name="reportName"
              value={reportName}
              onChange={this.handleInputChange}
              placeholder="Enter report name"
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="instance">Instance:</label>
            <select
              id="instance"
              name="instance"
              value={instance}
              onChange={this.handleInputChange}
            >
              <option value="">Select an instance</option>
              {INSTANCES.map((inst) => (
                <option key={inst} value={inst}>{inst}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="country">Country:</label>
            <select
              id="country"
              name="country"
              value={country}
              onChange={this.handleInputChange}
              disabled={!instance}
            >
              <option value="">Select a country</option>
              {COUNTRIES.map((cntry) => (
                <option key={cntry} value={cntry}>{cntry}</option>
              ))}
            </select>
          </div>
        </div>
      </form>
    );
  }
}

export default FeaturesForm;
