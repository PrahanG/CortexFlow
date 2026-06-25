from pydantic import BaseModel
from typing import Dict

class DashboardStats(BaseModel):
    total_documents: int
    completed_documents: int
    pending_documents: int
    failed_documents: int
    pii_compliant_count: int
    pii_flagged_count: int
    doc_type_distribution: Dict[str, int]
    risk_level_distribution: Dict[str, int]
