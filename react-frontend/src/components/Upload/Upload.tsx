import React, { useState, useRef } from 'react';
import './Upload.css';
import { apiService } from '../../services/apiService';
import { DocumentMetadata, ToastMessage } from '../../App';

interface UploadProps {
  onUploadSuccess: (metadata: DocumentMetadata) => void;
  showToast: (message: string, type: ToastMessage['type']) => void;
}

const Upload: React.FC<UploadProps> = ({ onUploadSuccess, showToast }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = async (file: File) => {
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      showToast('Please select a PDF file', 'error');
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      showToast('File size must be less than 10MB', 'error');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    // Simulate progress for better UX
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + 10;
      });
    }, 200);

    try {
      const result = await apiService.uploadDocument(file);
      
      if (result.success) {
        setUploadProgress(100);
        setTimeout(() => {
          onUploadSuccess(result.metadata);
        }, 500);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error: any) {
      clearInterval(progressInterval);
      setUploadProgress(0);
      showToast(`Upload error: ${error.message || 'Unknown error'}`, 'error');
      console.error('Upload error:', error);
    } finally {
      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress(0);
      }, 1000);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="upload-container">
      <div className="upload-card card">
        <div className="card-header">
          <div className="upload-header">
            <div className="upload-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="48" height="48" rx="12" fill="var(--color-primary)" fillOpacity="0.1"/>
                <path d="M24 16v16m-8-8l8-8 8 8" stroke="var(--color-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h2>Upload Contract Document</h2>
            <p>Upload a PDF contract to begin AI-powered risk analysis</p>
          </div>
        </div>

        <div className="card-body">
          <div
            className={`upload-area ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleBrowseClick}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />

            {!isUploading ? (
              <div className="upload-placeholder">
                <div className="upload-placeholder-icon">
                  <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect width="64" height="64" rx="16" fill="var(--color-gray-100)"/>
                    <path d="M20 32h24v2H20v-2zm0-4h24v2H20v-2zm0 8h18v2H20v-2z" fill="var(--color-gray-400)"/>
                  </svg>
                </div>
                <h3>Drop PDF file here or click to browse</h3>
                <p>Maximum file size: 10MB • Only PDF files supported</p>
                <button className="btn btn-primary" type="button">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 13h10v-1H3v1zm0-4h4v-1H3v1zm0-3h7v-1H3v1z" fill="currentColor"/>
                  </svg>
                  Choose File
                </button>
              </div>
            ) : (
              <div className="upload-progress">
                <div className="progress-icon">
                  <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="24" cy="24" r="20" stroke="var(--color-gray-200)" strokeWidth="4"/>
                    <circle 
                      cx="24" 
                      cy="24" 
                      r="20" 
                      stroke="var(--color-primary)" 
                      strokeWidth="4"
                      strokeDasharray={`${2 * Math.PI * 20}`}
                      strokeDashoffset={`${2 * Math.PI * 20 * (1 - uploadProgress / 100)}`}
                      strokeLinecap="round"
                      style={{ transition: 'stroke-dashoffset 0.3s ease' }}
                    />
                    <text x="24" y="28" textAnchor="middle" fontSize="12" fill="var(--color-primary)" fontWeight="600">
                      {uploadProgress}%
                    </text>
                  </svg>
                </div>
                <h3>Uploading and Processing...</h3>
                <p>Extracting text and analyzing document structure</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="upload-features">
        <div className="feature">
          <div className="feature-icon">🔍</div>
          <div className="feature-text">
            <h4>AI-Powered Analysis</h4>
            <p>Advanced NLP and MISTRAL7b model for accurate clause detection</p>
          </div>
        </div>
        <div className="feature">
          <div className="feature-icon">⚡</div>
          <div className="feature-text">
            <h4>Real-time Processing</h4>
            <p>Fast document processing with semantic understanding</p>
          </div>
        </div>
        <div className="feature">
          <div className="feature-icon">🛡️</div>
          <div className="feature-text">
            <h4>Risk Assessment</h4>
            <p>Comprehensive risk classification with confidence scores</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload; 