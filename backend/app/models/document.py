import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, 
        default=datetime.datetime.utcnow, 
        onupdate=datetime.datetime.utcnow
    )

    # Relationships
    logs: Mapped[List["ExecutionLog"]] = relationship(
        "ExecutionLog", 
        back_populates="document", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    metadata_records: Mapped[List["DocumentMetadata"]] = relationship(
        "DocumentMetadata", 
        back_populates="document", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    audits: Mapped[List["ComplianceAudit"]] = relationship(
        "ComplianceAudit", 
        back_populates="document", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    actions: Mapped[List["WorkflowAction"]] = relationship(
        "WorkflowAction", 
        back_populates="document", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    execution_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="logs")
