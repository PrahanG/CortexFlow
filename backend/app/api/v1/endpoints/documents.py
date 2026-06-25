import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentDetailResponse
from app.services.agent_service import process_document_workflow
from app.core.websocket_manager import manager

router = APIRouter()

# Directory for uploaded documents
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Handles PDF/text file upload, saves it, creates a database entry,
    and runs the LangGraph Swarm workflow in the background.
    """
    # Validation
    filename = file.filename
    _, ext = os.path.splitext(filename.lower())
    if ext not in [".pdf", ".txt", ".eml", ".email"]:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Only PDF, TXT, and Email logs are supported."
        )

    # Generate unique identifiers
    document_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{document_id}{ext}")
    
    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {str(e)}")
        
    # Get file size
    file_size = os.path.getsize(file_path)

    # Insert into MySQL
    document = Document(
        id=document_id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        status="PENDING"
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Trigger background agent pipeline
    background_tasks.add_task(process_document_workflow, document_id, file_path)

    return document

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns list of all uploaded documents.
    """
    result = await db.execute(
        select(Document).order_by(Document.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document_details(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves execution outputs, compliance reports, and logs for a document.
    """
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/{document_id}/export")
async def export_document_data(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Packs the original document, its metadata, compliance audit results,
    and the action template into a ZIP file.
    """
    import io
    import json
    import zipfile
    from fastapi import Response

    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Create the zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        # 1. Add original file if it exists
        if os.path.exists(document.file_path):
            zip_file.write(document.file_path, arcname=document.filename)
            
        # 2. Compile governance report JSON
        report = {
            "document_id": document.id,
            "filename": document.filename,
            "status": document.status,
            "created_at": str(document.created_at),
            "metadata": None,
            "compliance_audit": None,
            "workflow_action": None
        }
        
        if document.metadata_records:
            meta = document.metadata_records[0]
            report["metadata"] = {
                "doc_type": meta.doc_type,
                "confidence_score": meta.confidence_score,
                "extracted_properties": meta.extracted_properties,
                "sentiment": meta.sentiment,
                "readability_score": meta.readability_score,
                "entities": meta.entities
            }
            
        if document.audits:
            audit = document.audits[0]
            report["compliance_audit"] = {
                "pii_detected": audit.pii_detected,
                "risk_level": audit.risk_level,
                "pii_categories_found": audit.pii_categories_found,
                "violating_snippets": audit.violating_snippets,
                "compliance_status": audit.compliance_status
            }
            
        if document.actions:
            action = document.actions[0]
            report["workflow_action"] = {
                "recommended_action": action.recommended_action,
                "drafted_response": action.drafted_response,
                "action_status": action.action_status
            }
            
        zip_file.writestr("governance_report.json", json.dumps(report, indent=2))
        
        # 3. Add drafted communication template if available
        if document.actions and document.actions[0].drafted_response:
            zip_file.writestr("drafted_communication.txt", document.actions[0].drafted_response)
            
    content = zip_buffer.getvalue()
    
    # Generate download filename
    base_name, _ = os.path.splitext(document.filename)
    export_filename = f"{base_name}_governance_export.zip"
    
    return Response(
        content=content,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={export_filename}"}
    )

@router.websocket("/{document_id}/ws")
async def websocket_timeline_endpoint(
    websocket: WebSocket,
    document_id: str
):
    """
    WebSocket endpoint that streams timeline execution updates in real time.
    """
    await manager.connect(document_id, websocket)
    try:
        # Keep connection open, wait for client closure messages
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(document_id, websocket)
    except Exception as e:
        print(f"[WS] Connection error: {e}")
        manager.disconnect(document_id, websocket)
