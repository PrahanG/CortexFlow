import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DocumentInfo {
  id: string;
  filename: string;
  file_size: number;
  status: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface ExecutionLog {
  id: number;
  document_id: string;
  agent_name: string;
  status: string;
  message: string;
  execution_metadata?: any;
  timestamp: string;
}

export interface DocumentMetadata {
  doc_type: string;
  confidence_score: number;
  extracted_properties: any;
  sentiment?: string;
  readability_score?: number;
  entities?: any;
}

export interface ComplianceAudit {
  pii_detected: boolean;
  risk_level: string;
  pii_categories_found: string[];
  violating_snippets: string[];
  compliance_status: string;
}

export interface WorkflowAction {
  recommended_action: string;
  drafted_response: string;
  action_status: string;
}

export interface DocumentDetails extends DocumentInfo {
  logs: ExecutionLog[];
  metadata_records: DocumentMetadata[];
  audits: ComplianceAudit[];
  actions: WorkflowAction[];
}

export interface SearchResultItem {
  id: string;
  document_id: string;
  filename: string;
  content: string;
  distance: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResultItem[];
}

export interface DashboardStats {
  total_documents: number;
  completed_documents: number;
  pending_documents: number;
  failed_documents: number;
  pii_compliant_count: number;
  pii_flagged_count: number;
  doc_type_distribution: { [key: string]: number };
  risk_level_distribution: { [key: string]: number };
}

export interface ChatSource {
  document_id: string;
  filename: string;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
    ? 'http://127.0.0.1:8080/api/v1'
    : '/api/v1';

  constructor(private http: HttpClient) {}

  uploadDocument(file: File): Observable<DocumentInfo> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<DocumentInfo>(`${this.baseUrl}/documents/upload`, formData);
  }

  listDocuments(): Observable<DocumentInfo[]> {
    return this.http.get<DocumentInfo[]>(`${this.baseUrl}/documents/`);
  }

  getDocumentDetails(id: string): Observable<DocumentDetails> {
    return this.http.get<DocumentDetails>(`${this.baseUrl}/documents/${id}`);
  }

  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.baseUrl}/stats/`);
  }

  searchDocuments(query: string): Observable<SearchResponse> {
    const params = new HttpParams().set('q', query);
    return this.http.get<SearchResponse>(`${this.baseUrl}/search/`, { params });
  }

  chatWithSwarm(query: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.baseUrl}/chat/`, { query });
  }

  exportDocument(id: string): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/documents/${id}/export`, {
      responseType: 'blob'
    });
  }

  getAppConfig(): Observable<{ ws_url: string }> {
    return this.http.get<{ ws_url: string }>(`${this.baseUrl}/config`);
  }
}

