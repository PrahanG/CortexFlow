import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { ExecutionLog } from './api.service';

@Injectable({
  providedIn: 'root'
})
export class WebsocketService {
  private wsUrl = 'ws://127.0.0.1:8080/api/v1/documents';

  /**
   * Establishes a WebSocket connection for a specific document ID.
   * Returns an Observable streaming progress logs from the LangGraph swarm.
   */
  connect(documentId: string): Observable<ExecutionLog> {
    const logSubject = new Subject<ExecutionLog>();
    const socket = new WebSocket(`${this.wsUrl}/${documentId}/ws`);

    socket.onmessage = (event) => {
      try {
        const logData: ExecutionLog = JSON.parse(event.data);
        logSubject.next(logData);
      } catch (e) {
        console.error('[WS] Failed to parse message packet:', e);
      }
    };

    socket.onerror = (err) => {
      logSubject.error(err);
    };

    socket.onclose = () => {
      logSubject.complete();
    };

    // Return observable that handles teardown on unsubscribe
    return new Observable<ExecutionLog>((observer) => {
      const subscription = logSubject.subscribe(observer);
      return () => {
        subscription.unsubscribe();
        if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
          socket.close();
          console.log(`[WS] Connection closed for document: ${documentId}`);
        }
      };
    });
  }
}
