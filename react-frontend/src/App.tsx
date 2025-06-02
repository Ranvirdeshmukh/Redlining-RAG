import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header/Header';
import Upload from './components/Upload/Upload';
import Dashboard from './components/Dashboard/Dashboard';
import Results from './components/Results/Results';
import ClauseModal from './components/ClauseModal/ClauseModal';
import Toast from './components/common/Toast/Toast';
import LoadingOverlay from './components/common/LoadingOverlay/LoadingOverlay';
import { apiService } from './services/apiService';

export interface DocumentMetadata {
  doc_id: string;
  filename: string;
  total_chunks: number;
  total_clauses: number;
  word_count: number;
}

export interface AnalysisResult {
  risk_summary: { RED: number; AMBER: number; GREEN: number };
  risk_percentage: { RED: number; AMBER: number; GREEN: number };
  overall_risk: 'RED' | 'AMBER' | 'GREEN';
  total_clauses: number;
  recommendations: string[];
}

export interface ClassifiedClause {
  text: string;
  classification: {
    risk_level: 'RED' | 'AMBER' | 'GREEN';
    explanation: string;
    confidence: number;
    rule_based: any;
    rag_based: any;
    recommendations: string[];
  };
}

export interface ToastMessage {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

function App() {
  const [currentStep, setCurrentStep] = useState<'upload' | 'dashboard' | 'results'>('upload');
  const [documentMetadata, setDocumentMetadata] = useState<DocumentMetadata | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [classifiedClauses, setClassifiedClauses] = useState<ClassifiedClause[]>([]);
  const [redlinedHtml, setRedlinedHtml] = useState<string>('');
  const [selectedClause, setSelectedClause] = useState<ClassifiedClause | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    checkSystemHealth();
  }, []);

  const checkSystemHealth = async () => {
    try {
      await apiService.healthCheck();
    } catch (error) {
      showToast('System health check failed', 'warning');
    }
  };

  const showToast = (message: string, type: ToastMessage['type'] = 'info') => {
    const id = Date.now().toString();
    const newToast: ToastMessage = { id, message, type };
    setToasts(prev => [...prev, newToast]);
    
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 5000);
  };

  const handleUploadSuccess = (metadata: DocumentMetadata) => {
    setDocumentMetadata(metadata);
    setCurrentStep('dashboard');
    showToast('Document uploaded successfully!', 'success');
  };

  const handleAnalyze = async () => {
    if (!documentMetadata) return;

    setIsLoading(true);
    try {
      const result = await apiService.analyzeDocument(documentMetadata.doc_id);
      setAnalysisResult(result.analysis);
      setClassifiedClauses(result.classified_clauses);
      setRedlinedHtml(result.redlined_html);
      setCurrentStep('results');
      showToast('Analysis completed!', 'success');
    } catch (error) {
      showToast('Analysis failed. Please try again.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setCurrentStep('upload');
    setDocumentMetadata(null);
    setAnalysisResult(null);
    setClassifiedClauses([]);
    setRedlinedHtml('');
    setSelectedClause(null);
  };

  const handleExport = () => {
    if (!analysisResult || !documentMetadata) return;

    const exportData = {
      document: documentMetadata,
      analysis: analysisResult,
      clauses: classifiedClauses
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `contract-analysis-${documentMetadata.filename.replace('.pdf', '')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast('Analysis exported successfully!', 'success');
  };

  return (
    <div className="app">
      <Header />
      
      <main className="main-content">
        {currentStep === 'upload' && (
          <Upload onUploadSuccess={handleUploadSuccess} showToast={showToast} />
        )}
        
        {currentStep === 'dashboard' && documentMetadata && (
          <Dashboard
            documentMetadata={documentMetadata}
            analysisResult={analysisResult}
            onAnalyze={handleAnalyze}
            onReset={handleReset}
            onExport={handleExport}
            isLoading={isLoading}
          />
        )}
        
        {currentStep === 'results' && analysisResult && (
          <Results
            analysisResult={analysisResult}
            classifiedClauses={classifiedClauses}
            redlinedHtml={redlinedHtml}
            onClauseClick={setSelectedClause}
            onReset={handleReset}
            onExport={handleExport}
          />
        )}
      </main>

      {selectedClause && (
        <ClauseModal
          clause={selectedClause}
          onClose={() => setSelectedClause(null)}
        />
      )}

      {isLoading && <LoadingOverlay />}

      <div className="toast-container">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => setToasts(prev => prev.filter(t => t.id !== toast.id))}
          />
        ))}
      </div>
    </div>
  );
}

export default App;
