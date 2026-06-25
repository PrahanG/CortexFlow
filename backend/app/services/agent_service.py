import uuid
import datetime
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.document import Document, ExecutionLog
from app.models.metadata import DocumentMetadata, ComplianceAudit, WorkflowAction
from app.services.parser import parse_document, chunk_text
from app.services.vector_service import index_document_chunks
from app.agents.graph import swarm_graph
from app.core.websocket_manager import manager

async def create_log(
    db: AsyncSession, 
    document_id: str, 
    agent_name: str, 
    status: str, 
    message: str, 
    metadata: dict = None
) -> None:
    """
    Helper function to write an execution log to the DB and broadcast via WebSockets.
    """
    log_entry = ExecutionLog(
        document_id=document_id,
        agent_name=agent_name,
        status=status,
        message=message,
        execution_metadata=metadata
    )
    db.add(log_entry)
    await db.commit()
    
    # Broadcast to websocket
    await manager.broadcast_to_document(document_id, {
        "agent_name": agent_name,
        "status": status,
        "message": message,
        "execution_metadata": metadata,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

async def process_document_workflow(
    document_id: str, 
    file_path: str
) -> None:
    """
    Full async pipeline that coordinates Layout Parsing, Vector Indexing,
    LangGraph Swarm Execution, MySQL database saving, and WebSocket notifications.
    """
    from app.core.database import SessionLocal
    
    async with SessionLocal() as db:
        # Fetch the document object
        result = await db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()
        if not document:
            print(f"[ERROR] Document {document_id} not found in database.")
            return

        try:
            # --- 1. PARSING PHASE ---
            document.status = "PARSING"
            await db.commit()
            await create_log(
                db, document_id, "System", "IN_PROGRESS", 
                "Extracting text layout-aware structure using PyMuPDF..."
            )
            
            text = parse_document(file_path)
            
            # --- 2. VECTOR INDEXING PHASE ---
            document.status = "INDEXING"
            await db.commit()
            await create_log(
                db, document_id, "System", "IN_PROGRESS", 
                "Generating embeddings & indexing text chunks in ChromaDB..."
            )
            
            chunks = chunk_text(text)
            index_document_chunks(document_id, chunks)
            
            # --- 3. SWARM WORKFLOW PHASE ---
            document.status = "PROCESSING_SWARM"
            await db.commit()
            await create_log(
                db, document_id, "System", "IN_PROGRESS", 
                "Triggering LangGraph multi-agent swarm..."
            )
            
            # Initialize state
            state = {
                "document_id": document_id,
                "content": text,
                "doc_type": None,
                "confidence_score": None,
                "extracted_properties": None,
                "pii_detected": None,
                "risk_level": None,
                "pii_categories_found": None,
                "violating_snippets": None,
                "compliance_status": None,
                "recommended_action": None,
                "drafted_response": None,
                "logs": []
            }
            
            # Run graph nodes sequentially and stream updates
            async for output in swarm_graph.astream(state):
                for node_name, node_output in output.items():
                    # Grab latest node log if available
                    if "logs" in node_output and node_output["logs"]:
                        latest_log = node_output["logs"][-1]
                        await create_log(
                            db, document_id, 
                            latest_log["agent_name"], 
                            latest_log["status"], 
                            latest_log["message"], 
                            latest_log.get("execution_metadata")
                        )
                    # Merge outputs into our running state
                    state.update(node_output)

            # --- 4. PERSISTENCE & COMPLETION PHASE ---
            # 4a. Save classification metadata (Agent A)
            db_metadata = DocumentMetadata(
                id=str(uuid.uuid4()),
                document_id=document_id,
                doc_type=state.get("doc_type", "Other"),
                confidence_score=state.get("confidence_score", 1.0),
                extracted_properties=state.get("extracted_properties", {}),
                sentiment=state.get("sentiment", "Neutral"),
                readability_score=state.get("readability_score", 60.0),
                entities=state.get("entities", {})
            )
            db.add(db_metadata)
            
            # 4b. Save compliance audit logs (Agent B)
            db_audit = ComplianceAudit(
                id=str(uuid.uuid4()),
                document_id=document_id,
                pii_detected=state.get("pii_detected", False),
                risk_level=state.get("risk_level", "LOW"),
                pii_categories_found=state.get("pii_categories_found", []),
                violating_snippets=state.get("violating_snippets", []),
                compliance_status=state.get("compliance_status", "PASSED")
            )
            db.add(db_audit)
            
            # 4c. Save actions and draft communications (Agent C)
            db_action = WorkflowAction(
                id=str(uuid.uuid4()),
                document_id=document_id,
                recommended_action=state.get("recommended_action", "Manual Review Required"),
                drafted_response=state.get("drafted_response", ""),
                action_status="PENDING_REVIEW"
            )
            db.add(db_action)
            
            # 4d. Mark document as completed
            document.status = "COMPLETED"
            await db.commit()
            
            await create_log(
                db, document_id, "System", "SUCCESS", 
                "Autonomous document governance workflow successfully complete."
            )
            
        except Exception as e:
            traceback.print_exc()
            document.status = "FAILED"
            document.error_message = str(e)
            await db.commit()
            await create_log(
                db, document_id, "System", "FAILED", 
                f"Governance pipeline failed: {str(e)}", 
                {"traceback": traceback.format_exc()}
            )

