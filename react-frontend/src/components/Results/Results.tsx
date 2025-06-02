import React from 'react';
import './Results.css';
import { AnalysisResult, ClassifiedClause } from '../../App';

interface ResultsProps {
  analysisResult: AnalysisResult;
  classifiedClauses: ClassifiedClause[];
  redlinedHtml: string;
  onClauseClick: (clause: ClassifiedClause) => void;
  onReset: () => void;
  onExport: () => void;
}

const Results: React.FC<ResultsProps> = ({
  analysisResult,
  classifiedClauses,
  redlinedHtml,
  onClauseClick,
  onReset,
  onExport
}) => {
  const handleClauseClick = (index: number) => {
    if (classifiedClauses[index]) {
      onClauseClick(classifiedClauses[index]);
    }
  };

  return (
    <div className="results-container">
      <div className="results-header">
        <div className="header-content">
          <h2>📄 Redlined Contract Analysis</h2>
          <p>Click on any highlighted clause to see detailed risk analysis</p>
        </div>
        <div className="results-summary">
          <div className="summary-item">
            <span className="summary-label">Total Clauses:</span>
            <span className="summary-value">{analysisResult.total_clauses}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Overall Risk:</span>
            <span className={`risk-badge ${analysisResult.overall_risk.toLowerCase()}`}>
              {analysisResult.overall_risk}
            </span>
          </div>
        </div>
      </div>

      <div className="results-content">
        <div className="redlined-document card">
          <div className="card-header">
            <h3>Contract Document</h3>
            <div className="legend">
              <span className="legend-item">
                <span className="legend-color red"></span>
                High Risk
              </span>
              <span className="legend-item">
                <span className="legend-color amber"></span>
                Medium Risk
              </span>
              <span className="legend-item">
                <span className="legend-color green"></span>
                Low Risk
              </span>
            </div>
          </div>
          <div className="card-body">
            <div 
              className="redlined-content"
              dangerouslySetInnerHTML={{ __html: redlinedHtml }}
              onClick={(e) => {
                const target = e.target as HTMLElement;
                const clauseElement = target.closest('[data-clause-index]');
                if (clauseElement) {
                  const index = parseInt(clauseElement.getAttribute('data-clause-index') || '0');
                  handleClauseClick(index);
                }
              }}
            />
          </div>
        </div>
      </div>

      <div className="action-buttons">
        <button className="btn btn-secondary" onClick={onExport}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 11v3a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-3m3-7l3 3m0 0l3-3m-3 3V1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Export Results
        </button>
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

export default Results; 