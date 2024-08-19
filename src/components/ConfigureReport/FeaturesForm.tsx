import React, { Component } from 'react';
import "./FeaturesForm.css";

interface FeaturesFormProps {
  reportName: string;
  instance: string;
  country: string;
  onChange: (name: string, value: string) => void;
}

class FeaturesForm extends Component<FeaturesFormProps> {
  handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    this.props.onChange(name, value);
  };

  render() {
    const { reportName, instance, country } = this.props;

    return (
      <form className="features-form">
        <div>
          <label htmlFor="reportName">Report Name:</label>
          <input
            type="text"
            id="reportName"
            name="reportName"
            value={reportName}
            onChange={this.handleInputChange}
          />
        </div>
        <div>
          <label htmlFor="instance">Instance:</label>
          <input
            type="text"
            id="instance"
            name="instance"
            value={instance}
            onChange={this.handleInputChange}
          />
        </div>
        <div>
          <label htmlFor="country">Country:</label>
          <input
            type="text"
            id="country"
            name="country"
            value={country}
            onChange={this.handleInputChange}
          />
        </div>
      </form>
    );
  }
}

export default FeaturesForm;
