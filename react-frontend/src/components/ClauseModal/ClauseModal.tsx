import React from 'react';
import './ClauseModal.css';
import { ClassifiedClause } from '../../App';

interface ClauseModalProps {
  clause: ClassifiedClause;
  onClose: () => void;
}

const ClauseModal: React.FC<ClauseModalProps> = ({ clause, onClose }) => {
  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'RED': return '🔴';
      case 'AMBER': return '🟡';
      case 'GREEN': return '🟢';
      default: return '⚪';
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'RED': return 'var(--color-red)';
      case 'AMBER': return 'var(--color-amber)';
      case 'GREEN': return 'var(--color-green)';
      default: return 'var(--color-gray-500)';
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content">
        <div className="modal-header">
          <div className="modal-title">
            <h3>Clause Analysis Details</h3>
            <div className="risk-indicator" style={{ color: getRiskColor(clause.classification.risk_level) }}>
              {getRiskIcon(clause.classification.risk_level)} {clause.classification.risk_level} RISK
            </div>
          </div>
          <button className="close-button" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>

        <div className="modal-body">
          <div className="clause-text">
            <h4>📄 Clause Text</h4>
            <div className="clause-content">
              {clause.text}
            </div>
          </div>

          <div className="analysis-details">
            <div className="detail-section">
              <h4>🎯 Risk Assessment</h4>
              <div className="confidence-score">
                <span>Confidence Score:</span>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill" 
                    style={{ 
                      width: `${clause.classification.confidence * 100}%`,
                      backgroundColor: getRiskColor(clause.classification.risk_level)
                    }}
                  ></div>
                </div>
                <span>{Math.round(clause.classification.confidence * 100)}%</span>
              </div>
            </div>

            <div className="detail-section">
              <h4>💡 Explanation</h4>
              <p>{clause.classification.explanation}</p>
            </div>

            <div className="detail-section">
              <h4>📋 Recommendations</h4>
              <ul>
                {clause.classification.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>

            <div className="analysis-comparison">
              <div className="comparison-item">
                <h5>🤖 Rule-based Analysis</h5>
                <div className="comparison-details">
                  <span className="comparison-result">
                    {clause.classification.rule_based?.risk_level || 'N/A'}
                  </span>
                  <span className="comparison-confidence">
                    {clause.classification.rule_based?.confidence 
                      ? `${Math.round(clause.classification.rule_based.confidence * 100)}%`
                      : 'N/A'
                    }
                  </span>
                </div>
              </div>
              <div className="comparison-item">
                <h5>🧠 RAG Analysis</h5>
                <div className="comparison-details">
                  <span className="comparison-result">
                    {clause.classification.rag_based?.risk_level || 'N/A'}
                  </span>
                  <span className="comparison-confidence">
                    {clause.classification.rag_based?.confidence 
                      ? `${Math.round(clause.classification.rag_based.confidence * 100)}%`
                      : 'N/A'
                    }
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClauseModal; 