import axios from 'axios';

const API_BASE_URL = process.env.NODE_ENV === 'production' ? 'http://localhost:8000' : '';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for analysis
});

export interface UploadResponse {
  success: boolean;
  message: string;
  doc_id: string;
  metadata: {
    doc_id: string;
    filename: string;
    total_chunks: number;
    total_clauses: number;
    word_count: number;
  };
}

export interface AnalysisResponse {
  success: boolean;
  doc_id: string;
  analysis: {
    risk_summary: { RED: number; AMBER: number; GREEN: number };
    risk_percentage: { RED: number; AMBER: number; GREEN: number };
    overall_risk: 'RED' | 'AMBER' | 'GREEN';
    total_clauses: number;
    recommendations: string[];
  };
  classified_clauses: Array<{
    text: string;
    classification: {
      risk_level: 'RED' | 'AMBER' | 'GREEN';
      explanation: string;
      confidence: number;
      rule_based: any;
      rag_based: any;
      recommendations: string[];
    };
  }>;
  redlined_html: string;
}

export interface SearchResponse {
  success: boolean;
  query: string;
  results: Array<{
    text: string;
    metadata: any;
    distance: number;
    id: string;
  }>;
}

export interface ClassifyTextResponse {
  success: boolean;
  classification: {
    risk_level: 'RED' | 'AMBER' | 'GREEN';
    explanation: string;
    confidence: number;
    recommendations: string[];
  };
}

class ApiService {
  async uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async analyzeDocument(docId: string): Promise<AnalysisResponse> {
    const response = await api.post<AnalysisResponse>(`/analyze/${docId}`);
    return response.data;
  }

  async searchClauses(query: string, limit: number = 10): Promise<SearchResponse> {
    const response = await api.get<SearchResponse>('/search', {
      params: { query, limit },
    });
    return response.data;
  }

  async classifyText(text: string): Promise<ClassifyTextResponse> {
    const response = await api.post<ClassifyTextResponse>('/classify-text', {
      text,
    });
    return response.data;
  }

  async healthCheck(): Promise<{ status: string; message: string }> {
    const response = await api.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService(); 