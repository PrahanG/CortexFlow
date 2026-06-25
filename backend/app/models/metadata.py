import datetime
from sqlalchemy import String, ForeignKey, DateTime, JSON, Boolean, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class DocumentMetadata(Base):
    __tablename__ = "document_metadata"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    extracted_properties: Mapped[dict] = mapped_column(JSON, nullable=False)
    sentiment: Mapped[str] = mapped_column(String(50), nullable=True)
    readability_score: Mapped[float] = mapped_column(Float, nullable=True)
    entities: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="metadata_records")

class ComplianceAudit(Base):
    __tablename__ = "compliance_audits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False)
    pii_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    pii_categories_found: Mapped[dict] = mapped_column(JSON, nullable=False)  # JSON array
    violating_snippets: Mapped[dict] = mapped_column(JSON, nullable=False)     # JSON array
    compliance_status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="audits")

class WorkflowAction(Base):
    __tablename__ = "workflow_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False)
    recommended_action: Mapped[str] = mapped_column(String(100), nullable=False)
    drafted_response: Mapped[str] = mapped_column(Text, nullable=False)
    action_status: Mapped[str] = mapped_column(String(50), default="PENDING_REVIEW")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="actions")
