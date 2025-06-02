// Contract Redlining RAG System - JavaScript

let currentDocumentId = null;
let analysisData = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    checkSystemHealth();
});

function initializeEventListeners() {
    // File input change
    document.getElementById('fileInput').addEventListener('change', handleFileSelect);
    
    // Drag and drop
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Click to upload
    uploadArea.addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
    
    // Modal close
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('clauseModal');
        if (event.target === modal) {
            closeModal();
        }
    });
}

// File handling functions
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

// Upload file function
async function uploadFile(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
        showToast('File size must be less than 10MB', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showUploadProgress();
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentDocumentId = result.doc_id;
            hideUploadProgress();
            showAnalysisSection(result.metadata);
            showToast('Document uploaded successfully!', 'success');
        } else {
            throw new Error(result.detail || 'Upload failed');
        }
    } catch (error) {
        hideUploadProgress();
        showToast(`Upload error: ${error.message}`, 'error');
        console.error('Upload error:', error);
    }
}

// Analysis functions
async function analyzeDocument() {
    if (!currentDocumentId) {
        showToast('No document uploaded', 'error');
        return;
    }
    
    showLoadingOverlay();
    
    try {
        const response = await fetch(`/analyze/${currentDocumentId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            analysisData = result;
            hideLoadingOverlay();
            displayAnalysisResults(result);
            showResultsSection(result);
            showToast('Analysis completed!', 'success');
        } else {
            throw new Error(result.detail || 'Analysis failed');
        }
    } catch (error) {
        hideLoadingOverlay();
        showToast(`Analysis error: ${error.message}`, 'error');
        console.error('Analysis error:', error);
    }
}

// UI Display functions
function showAnalysisSection(metadata) {
    document.getElementById('analysisSection').style.display = 'block';
    
    const documentInfo = document.getElementById('documentInfo');
    documentInfo.innerHTML = `
        <strong>📄 ${metadata.filename}</strong><br>
        📊 Total Chunks: ${metadata.total_chunks} | 
        ⚖️ Contract Clauses: ${metadata.total_clauses} | 
        📝 Word Count: ${metadata.word_count.toLocaleString()}
    `;
}

function displayAnalysisResults(result) {
    const analysis = result.analysis;
    
    // Update risk counts
    document.getElementById('redCount').textContent = analysis.risk_summary.RED;
    document.getElementById('amberCount').textContent = analysis.risk_summary.AMBER;
    document.getElementById('greenCount').textContent = analysis.risk_summary.GREEN;
    
    // Update overall risk badge
    const overallBadge = document.getElementById('overallRiskBadge');
    overallBadge.textContent = `${analysis.overall_risk} RISK`;
    overallBadge.className = `overall-risk-badge ${analysis.overall_risk.toLowerCase()}`;
    
    // Update recommendations
    const recommendationsDiv = document.getElementById('recommendations');
    if (analysis.recommendations && analysis.recommendations.length > 0) {
        recommendationsDiv.innerHTML = `
            <h4>📋 Recommendations:</h4>
            <ul>
                ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        `;
    }
    
    // Show export button
    document.getElementById('exportBtn').style.display = 'inline-flex';
}

function showResultsSection(result) {
    document.getElementById('resultsSection').style.display = 'block';
    
    const redlinedDocument = document.getElementById('redlinedDocument');
    redlinedDocument.innerHTML = result.redlined_html;
    
    // Add click listeners to clauses
    addClauseClickListeners(result.classified_clauses);
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ 
        behavior: 'smooth' 
    });
}

function addClauseClickListeners(clauses) {
    const clauseElements = document.querySelectorAll('.redlined-document > div[class*="risk-"]');
    
    clauseElements.forEach((element, index) => {
        element.addEventListener('click', () => {
            if (clauses[index]) {
                showClauseModal(clauses[index]);
            }
        });
    });
}

function showClauseModal(clause) {
    const modal = document.getElementById('clauseModal');
    const modalBody = document.getElementById('modalBody');
    
    const classification = clause.classification;
    const riskColor = {
        'RED': '#e74c3c',
        'AMBER': '#f39c12',
        'GREEN': '#27ae60'
    }[classification.risk_level];
    
    modalBody.innerHTML = `
        <div style="margin-bottom: 20px;">
            <div style="background: ${riskColor}; color: white; padding: 10px; border-radius: 8px; margin-bottom: 15px;">
                <h4>${classification.risk_level} RISK LEVEL</h4>
                <p>Confidence: ${(classification.confidence * 100).toFixed(1)}%</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h5>📄 Clause Text:</h5>
                <p style="font-style: italic; line-height: 1.6;">"${clause.text}"</p>
            </div>
            
            <div style="margin-bottom: 15px;">
                <h5>🔍 Analysis:</h5>
                <p>${classification.explanation}</p>
            </div>
            
            <div style="margin-bottom: 15px;">
                <h5>💡 Recommendations:</h5>
                <ul>
                    ${classification.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
            
            ${classification.rule_based ? `
                <div style="background: #e3f2fd; padding: 10px; border-radius: 8px; font-size: 0.9em;">
                    <strong>Rule-based Analysis:</strong> ${classification.rule_based.explanation}<br>
                    <strong>Matched Keywords:</strong> ${classification.rule_based.matched_keywords.join(', ') || 'None'}
                </div>
            ` : ''}
        </div>
    `;
    
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('clauseModal').style.display = 'none';
}

// Utility functions
function showUploadProgress() {
    document.getElementById('uploadProgress').style.display = 'block';
    animateProgress();
}

function hideUploadProgress() {
    document.getElementById('uploadProgress').style.display = 'none';
    document.getElementById('progressFill').style.width = '0%';
}

function animateProgress() {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 95) {
            progress = 95;
            clearInterval(interval);
        }
        
        progressFill.style.width = `${progress}%`;
        
        if (progress < 30) {
            progressText.textContent = 'Uploading file...';
        } else if (progress < 60) {
            progressText.textContent = 'Processing document...';
        } else if (progress < 90) {
            progressText.textContent = 'Extracting text...';
        } else {
            progressText.textContent = 'Finalizing...';
        }
    }, 200);
}

function showLoadingOverlay() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoadingOverlay() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas ${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

function getToastIcon(type) {
    switch (type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        default: return 'fa-info-circle';
    }
}

// Export functions
function exportResults() {
    if (!analysisData) {
        showToast('No analysis data to export', 'error');
        return;
    }
    
    const exportData = {
        document_id: analysisData.doc_id,
        analysis_summary: analysisData.analysis,
        classified_clauses: analysisData.classified_clauses,
        export_timestamp: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `contract_analysis_${analysisData.doc_id}.json`;
    link.click();
    
    showToast('Analysis exported successfully!', 'success');
}

// Reset function
function resetApp() {
    currentDocumentId = null;
    analysisData = null;
    
    document.getElementById('analysisSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('fileInput').value = '';
    
    // Reset form
    document.getElementById('uploadProgress').style.display = 'none';
    document.getElementById('progressFill').style.width = '0%';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    showToast('Ready for new analysis', 'info');
}

// Health check
async function checkSystemHealth() {
    try {
        const response = await fetch('/health');
        const health = await response.json();
        
        if (health.status === 'healthy') {
            console.log('✅ System is healthy');
            
            // Check model status
            const modelsLoaded = Object.values(health.models_loaded).every(Boolean);
            if (!modelsLoaded) {
                showToast('⚠️ Some models are still loading...', 'warning');
            }
        } else {
            showToast('⚠️ System health check failed', 'warning');
        }
    } catch (error) {
        console.warn('Health check failed:', error);
        showToast('⚠️ Unable to verify system status', 'warning');
    }
}

// Search functionality (bonus feature)
async function searchClauses(query) {
    try {
        const response = await fetch(`/search?query=${encodeURIComponent(query)}&limit=10`);
        const result = await response.json();
        
        if (result.success) {
            return result.results;
        } else {
            throw new Error(result.detail || 'Search failed');
        }
    } catch (error) {
        showToast(`Search error: ${error.message}`, 'error');
        return [];
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl+U for upload
    if (event.ctrlKey && event.key === 'u') {
        event.preventDefault();
        document.getElementById('fileInput').click();
    }
    
    // Ctrl+A for analyze
    if (event.ctrlKey && event.key === 'a' && currentDocumentId) {
        event.preventDefault();
        analyzeDocument();
    }
    
    // Escape to close modal
    if (event.key === 'Escape') {
        closeModal();
    }
});

// Performance monitoring
let performanceMetrics = {
    uploadTime: 0,
    analysisTime: 0,
    renderTime: 0
};

function startTimer(metric) {
    performanceMetrics[metric] = Date.now();
}

function endTimer(metric) {
    if (performanceMetrics[metric]) {
        const duration = Date.now() - performanceMetrics[metric];
        console.log(`⏱️ ${metric}: ${duration}ms`);
        return duration;
    }
    return 0;
} 