from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.document import Document
from app.models.metadata import DocumentMetadata, ComplianceAudit
from app.schemas.stats import DashboardStats

router = APIRouter()

@router.get("", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Computes real-time aggregates for dashboard widgets (Total files, status breakdown,
    PII ratios, and document classifications).
    """
    # 1. Base counts
    total = (await db.execute(select(func.count(Document.id)))).scalar() or 0
    completed = (await db.execute(
        select(func.count(Document.id)).where(Document.status == "COMPLETED")
    )).scalar() or 0
    failed = (await db.execute(
        select(func.count(Document.id)).where(Document.status == "FAILED")
    )).scalar() or 0
    pending = total - completed - failed
    
    # 2. Compliance PII distribution
    compliant = (await db.execute(
        select(func.count(ComplianceAudit.id)).where(ComplianceAudit.pii_detected == False)
    )).scalar() or 0
    flagged = (await db.execute(
        select(func.count(ComplianceAudit.id)).where(ComplianceAudit.pii_detected == True)
    )).scalar() or 0
    
    # 3. Document types distribution
    doc_type_distribution = {}
    type_results = await db.execute(
        select(DocumentMetadata.doc_type, func.count(DocumentMetadata.id)).group_by(DocumentMetadata.doc_type)
    )
    for row in type_results:
        doc_type_distribution[row[0]] = row[1]
        
    # 4. Risk level distribution
    risk_level_distribution = {}
    risk_results = await db.execute(
        select(ComplianceAudit.risk_level, func.count(ComplianceAudit.id)).group_by(ComplianceAudit.risk_level)
    )
    for row in risk_results:
        risk_level_distribution[row[0]] = row[1]
        
    return DashboardStats(
        total_documents=total,
        completed_documents=completed,
        pending_documents=pending,
        failed_documents=failed,
        pii_compliant_count=compliant,
        pii_flagged_count=flagged,
        doc_type_distribution=doc_type_distribution,
        risk_level_distribution=risk_level_distribution
    )
