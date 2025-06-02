import React from 'react';
import './Dashboard.css';
import { DocumentMetadata, AnalysisResult } from '../../App';

interface DashboardProps {
  documentMetadata: DocumentMetadata;
  analysisResult: AnalysisResult | null;
  onAnalyze: () => void;
  onReset: () => void;
  onExport: () => void;
  isLoading: boolean;
}

const Dashboard: React.FC<DashboardProps> = ({
  documentMetadata,
  analysisResult,
  onAnalyze,
  onReset,
  onExport,
  isLoading
}) => {
  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="header-content">
          <h2>Risk Analysis Dashboard</h2>
          <p>Document uploaded and ready for analysis</p>
        </div>
      </div>

      <div className="document-info card">
        <div className="card-header">
          <h3>Document Information</h3>
        </div>
        <div className="card-body">
          <div className="document-details">
            <div className="detail-item">
              <span className="detail-label">📄 Filename</span>
              <span className="detail-value">{documentMetadata.filename}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">📊 Total Chunks</span>
              <span className="detail-value">{documentMetadata.total_chunks.toLocaleString()}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">⚖️ Contract Clauses</span>
              <span className="detail-value">{documentMetadata.total_clauses.toLocaleString()}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">📝 Word Count</span>
              <span className="detail-value">{documentMetadata.word_count.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>

      {analysisResult && (
        <>
          <div className="risk-summary">
            <div className="risk-card card risk-red-bg">
              <div className="risk-icon">🔴</div>
              <div className="risk-details">
                <h3>HIGH RISK</h3>
                <span className="risk-count">{analysisResult.risk_summary.RED}</span>
                <p>Requires immediate attention</p>
              </div>
            </div>
            
            <div className="risk-card card risk-amber-bg">
              <div className="risk-icon">🟡</div>
              <div className="risk-details">
                <h3>MEDIUM RISK</h3>
                <span className="risk-count">{analysisResult.risk_summary.AMBER}</span>
                <p>Review recommended</p>
              </div>
            </div>
            
            <div className="risk-card card risk-green-bg">
              <div className="risk-icon">🟢</div>
              <div className="risk-details">
                <h3>LOW RISK</h3>
                <span className="risk-count">{analysisResult.risk_summary.GREEN}</span>
                <p>Generally acceptable</p>
              </div>
            </div>
          </div>

          <div className="overall-assessment card">
            <div className="card-header">
              <div className="assessment-header">
                <h3>⚖️ Overall Document Risk</h3>
                <span className={`overall-risk-badge ${analysisResult.overall_risk.toLowerCase()}`}>
                  {analysisResult.overall_risk} RISK
                </span>
              </div>
            </div>
            <div className="card-body">
              <div className="recommendations">
                <h4>📋 Recommendations:</h4>
                <ul>
                  {analysisResult.recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </>
      )}

      <div className="action-buttons">
        {!analysisResult ? (
          <button 
            className="btn btn-primary" 
            onClick={onAnalyze}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="loading-spinner"></div>
                Analyzing...
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 1v6l4-4m-4 4L4 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Analyze Document
              </>
            )}
          </button>
        ) : (
          <button className="btn btn-secondary" onClick={onExport}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 11v3a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-3m3-7l3 3m0 0l3-3m-3 3V1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Export Results
          </button>
        )}
        
        <button className="btn btn-secondary" onClick={onReset}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 4v6h6m8-6v6H9m6-9a9 9 0 1 1-9 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          New Analysis
        </button>
      </div>
    </div>
  );
};

export default Dashboard; 