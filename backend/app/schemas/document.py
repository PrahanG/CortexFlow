from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class ExecutionLogResponse(BaseModel):
    id: int
    document_id: str
    agent_name: str
    status: str
    message: str
    execution_metadata: Optional[Any] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class DocumentMetadataResponse(BaseModel):
    doc_type: str
    confidence_score: float
    extracted_properties: Any
    sentiment: Optional[str] = None
    readability_score: Optional[float] = None
    entities: Optional[Any] = None

    class Config:
        from_attributes = True

class ComplianceAuditResponse(BaseModel):
    pii_detected: bool
    risk_level: str
    pii_categories_found: Any
    violating_snippets: Any
    compliance_status: str

    class Config:
        from_attributes = True

class WorkflowActionResponse(BaseModel):
    recommended_action: str
    drafted_response: str
    action_status: str

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentDetailResponse(DocumentResponse):
    logs: List[ExecutionLogResponse] = []
    metadata_records: List[DocumentMetadataResponse] = []
    audits: List[ComplianceAuditResponse] = []
    actions: List[WorkflowActionResponse] = []
