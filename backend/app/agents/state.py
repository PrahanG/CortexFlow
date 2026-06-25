from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    # Inputs
    document_id: str
    content: str
    
    # Agent A (Triage / Classification) Outputs
    doc_type: Optional[str]
    confidence_score: Optional[float]
    extracted_properties: Optional[Dict[str, Any]]
    
    # NLP Enrichment Agent Outputs
    sentiment: Optional[str]
    readability_score: Optional[float]
    entities: Optional[Dict[str, Any]]
    
    # Agent B (Privacy / Compliance) Outputs
    pii_detected: Optional[bool]
    risk_level: Optional[str]
    pii_categories_found: Optional[List[str]]
    violating_snippets: Optional[List[str]]
    compliance_status: Optional[str]
    
    # Agent C (Action Router) Outputs
    recommended_action: Optional[str]
    drafted_response: Optional[str]
    
    # Swarm Log Collector
    # Used for recording node statuses and publishing WebSocket updates
    logs: List[Dict[str, Any]]
