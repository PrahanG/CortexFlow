import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { ApiService, DocumentInfo, DocumentDetails, DashboardStats, SearchResultItem, ExecutionLog } from './core/services/api.service';
import { WebsocketService } from './core/services/websocket.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'CortexFlow';

  // Core Data Arrays
  documents: DocumentInfo[] = [];
  selectedDocument: DocumentDetails | null = null;
  stats: DashboardStats | null = null;

  // Search Variables (RAG)
  searchQuery: string = '';
  searchResults: SearchResultItem[] = [];
  isSearching: boolean = false;

  // Upload Management
  isDragOver: boolean = false;
  isUploading: boolean = false;
  uploadError: string | null = null;

  // Active Websocket Timeline
  activeJobId: string | null = null;
  activeTimelineLogs: ExecutionLog[] = [];
  private wsSubscription: Subscription | null = null;

  // EIM Chatbot State
  isChatOpen: boolean = false;
  chatInput: string = '';
  isChatTyping: boolean = false;
  chatMessages: Array<{ sender: 'user' | 'bot'; text: string; sources?: any[] }> = [];

  constructor(
    private apiService: ApiService,
    private wsService: WebsocketService
  ) {}

  ngOnInit() {
    this.refreshData();
  }

  ngOnDestroy() {
    this.disconnectWebSocket();
  }

  // Refresh lists and telemetry stats
  refreshData() {
    this.apiService.listDocuments().subscribe({
      next: (docs) => {
        this.documents = docs;
        // If there's an active job, verify its status in the list
        if (this.activeJobId) {
          const activeDoc = docs.find(d => d.id === this.activeJobId);
          if (activeDoc && (activeDoc.status === 'COMPLETED' || activeDoc.status === 'FAILED')) {
            this.activeJobId = null;
            this.disconnectWebSocket();
            this.refreshData();
          }
        }
      },
      error: (err) => console.error('Failed to load documents', err)
    });

    this.apiService.getDashboardStats().subscribe({
      next: (stats) => this.stats = stats,
      error: (err) => console.error('Failed to load dashboard metrics', err)
    });
  }

  // Load detailed audit reports & timeline history
  viewDocumentDetails(docId: string) {
    this.apiService.getDocumentDetails(docId).subscribe({
      next: (details) => {
        this.selectedDocument = details;
        // If the document is currently executing and not yet tracked, hook to its socket
        if (details.status !== 'COMPLETED' && details.status !== 'FAILED') {
          this.trackActiveSwarmTimeline(details.id);
        }
      },
      error: (err) => console.error('Failed to retrieve document details', err)
    });
  }

  // Drag-and-Drop event handlers
  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.handleFileUpload(files[0]);
    }
  }

  onFileSelected(event: any) {
    const files = event.target.files;
    if (files && files.length > 0) {
      this.handleFileUpload(files[0]);
    }
  }

  // Upload Logic and Pipeline Initiation
  private handleFileUpload(file: File) {
    this.isUploading = true;
    this.uploadError = null;

    this.apiService.uploadDocument(file).subscribe({
      next: (doc) => {
        this.isUploading = false;
        this.refreshData();
        // Immediately view details and connect the WebSocket to stream layout parsing and agents execution
        this.viewDocumentDetails(doc.id);
        this.trackActiveSwarmTimeline(doc.id);
      },
      error: (err) => {
        this.isUploading = false;
        this.uploadError = err.error?.detail || 'Failed to upload document.';
        console.error('File upload error', err);
      }
    });
  }

  // Real-time swarm monitoring via WebSockets
  private trackActiveSwarmTimeline(docId: string) {
    this.disconnectWebSocket();
    this.activeJobId = docId;
    this.activeTimelineLogs = [];

    // If viewing the newly created doc, pre-populate logs from database first if any exist
    if (this.selectedDocument && this.selectedDocument.id === docId) {
      this.activeTimelineLogs = [...this.selectedDocument.logs];
    }

    this.wsSubscription = this.wsService.connect(docId).subscribe({
      next: (log) => {
        // Append log to list
        this.activeTimelineLogs = [...this.activeTimelineLogs, log];
        // Scroll timeline log box if needed
        setTimeout(() => this.scrollToBottom('timeline-box'), 50);

        // Update selected document's logs if it is currently open
        if (this.selectedDocument && this.selectedDocument.id === docId) {
          this.selectedDocument.logs = [...this.selectedDocument.logs, log];
        }

        // If the workflow is marked successful or failed, disconnect and refresh stats
        if (log.status === 'SUCCESS' || log.status === 'FAILED') {
          setTimeout(() => {
            this.activeJobId = null;
            this.disconnectWebSocket();
            this.refreshData();
            // Reload details to display extracted metadata and compliance reports
            this.viewDocumentDetails(docId);
          }, 1500);
        }
      },
      error: (err) => {
        console.error('[WS] Connection error or closed:', err);
        this.disconnectWebSocket();
      }
    });
  }

  private disconnectWebSocket() {
    if (this.wsSubscription) {
      this.wsSubscription.unsubscribe();
      this.wsSubscription = null;
    }
  }

  // RAG Search Logic
  triggerRagSearch() {
    if (!this.searchQuery.trim()) {
      this.searchResults = [];
      return;
    }

    this.isSearching = true;
    this.apiService.searchDocuments(this.searchQuery).subscribe({
      next: (response) => {
        this.searchResults = response.results;
        this.isSearching = false;
      },
      error: (err) => {
        console.error('Search query failed', err);
        this.isSearching = false;
      }
    });
  }

  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  private scrollToBottom(elementId: string) {
    const element = document.getElementById(elementId);
    if (element) {
      element.scrollTop = element.scrollHeight;
    }
  }

  // EIM Chatbot Handlers
  toggleChat() {
    this.isChatOpen = !this.isChatOpen;
    if (this.isChatOpen) {
      setTimeout(() => this.scrollToBottom('chat-body'), 50);
    }
  }

  quickQuestion(text: string) {
    this.chatInput = text;
    this.sendChatMessage();
  }

  sendChatMessage() {
    const query = this.chatInput.trim();
    if (!query || this.isChatTyping) return;

    // Push user message
    this.chatMessages.push({ sender: 'user', text: query });
    this.chatInput = '';
    this.isChatTyping = true;
    setTimeout(() => this.scrollToBottom('chat-body'), 50);

    // Call API
    this.apiService.chatWithSwarm(query).subscribe({
      next: (res) => {
        this.chatMessages.push({
          sender: 'bot',
          text: res.answer,
          sources: res.sources
        });
        this.isChatTyping = false;
        setTimeout(() => this.scrollToBottom('chat-body'), 50);
      },
      error: (err) => {
        console.error('Chat error', err);
        this.chatMessages.push({
          sender: 'bot',
          text: 'Sorry, I encountered an error communicating with the document swarm.'
        });
        this.isChatTyping = false;
        setTimeout(() => this.scrollToBottom('chat-body'), 50);
      }
    });
  }

  // Feature 3: Donut Segment Calculations
  getDonutSegments() {
    if (!this.stats || !this.stats.doc_type_distribution) return [];
    
    const dist = this.stats.doc_type_distribution;
    const total = Object.values(dist).reduce((a, b) => a + b, 0);
    if (total === 0) return [];
    
    const colors = ['#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#EC4899'];
    let cumulativePercentage = 0;
    
    return Object.entries(dist).map(([label, count], index) => {
      const percentage = (count / total) * 100;
      const dashArray = `${(percentage / 100) * 251.2} 251.2`;
      const dashOffset = 251.2 - (cumulativePercentage / 100) * 251.2;
      cumulativePercentage += percentage;
      
      return {
        label,
        count,
        percentage,
        dashArray,
        dashOffset,
        color: colors[index % colors.length]
      };
    });
  }

  // Feature 3: Risk Level Bar Calculations
  getRiskLevels() {
    if (!this.stats || !this.stats.risk_level_distribution) return [];
    
    const dist = this.stats.risk_level_distribution;
    const levels = ['Low', 'Medium', 'High'];
    const colors: { [key: string]: string } = {
      'low': 'green',
      'medium': 'yellow',
      'high': 'red'
    };
    
    let total = 0;
    levels.forEach(lvl => {
      const count = dist[lvl] || dist[lvl.toUpperCase()] || dist[lvl.toLowerCase()] || 0;
      total += count;
    });
    
    if (total === 0) {
      return levels.map(lvl => ({
        level: lvl,
        count: 0,
        percentage: 0,
        colorClass: colors[lvl.toLowerCase()]
      }));
    }
    
    return levels.map(lvl => {
      const count = dist[lvl] || dist[lvl.toUpperCase()] || dist[lvl.toLowerCase()] || 0;
      const percentage = (count / total) * 100;
      return {
        level: lvl,
        count,
        percentage,
        colorClass: colors[lvl.toLowerCase()]
      };
    });
  }

  // Feature 4: EIM Ingestion Simulator (Export Zip)
  exportDocumentData(docId: string, filename: string) {
    this.apiService.exportDocument(docId).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const baseName = filename.replace(/\.[^/.]+$/, "");
        a.download = `${baseName}_governance_export.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      },
      error: (err) => console.error('Failed to export document data', err)
    });
  }
}

