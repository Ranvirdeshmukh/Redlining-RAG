import React from 'react';
import './LoadingOverlay.css';

const LoadingOverlay: React.FC = () => {
  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <div className="loading-spinner-large">
          <svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="30" cy="30" r="25" stroke="var(--color-gray-200)" strokeWidth="4"/>
            <circle 
              cx="30" 
              cy="30" 
              r="25" 
              stroke="var(--color-primary)" 
              strokeWidth="4"
              strokeDasharray="157"
              strokeDashoffset="39"
              strokeLinecap="round"
              className="spinner-circle"
            />
          </svg>
        </div>
        <h3>Analyzing Contract...</h3>
        <p>AI is processing your document and identifying risk factors</p>
        <div className="loading-steps">
          <div className="step active">
            <div className="step-dot"></div>
            <span>Extracting clauses</span>
          </div>
          <div className="step active">
            <div className="step-dot"></div>
            <span>Running AI analysis</span>
          </div>
          <div className="step">
            <div className="step-dot"></div>
            <span>Generating results</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingOverlay; 