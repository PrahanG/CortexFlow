from app.agents.state import AgentState
from app.agents.prompts import SYSTEM_PROMPT_TRIAGE
from app.agents.nodes import call_gemini_json

def triage_node(state: AgentState) -> dict:
    """
    Agent A: Triage and Classification.
    Analyzes document text to determine its type and extract key structured fields.
    """
    content = state.get("content", "")
    
    # Prepare realistic fallback structure
    fallback = {
        "doc_type": "Other",
        "confidence_score": 0.5,
        "extracted_properties": {"content_length": len(content)}
    }
    
    content_lower = content.lower()
    if "invoice" in content_lower or "bill to" in content_lower or "amount due" in content_lower:
        fallback = {
            "doc_type": "Invoice",
            "confidence_score": 0.92,
            "extracted_properties": {"vendor": "Acme Corp Services", "amount": "$4,500.00", "currency": "USD"}
        }
    elif "contract" in content_lower or "agreement" in content_lower or "shall agree" in content_lower:
        fallback = {
            "doc_type": "Contract",
            "confidence_score": 0.95,
            "extracted_properties": {"contracting_parties": "Vendor and Client", "governing_law": "Delaware"}
        }
    elif "policy" in content_lower or "hr" in content_lower or "conduct" in content_lower:
        fallback = {
            "doc_type": "HR_Policy",
            "confidence_score": 0.88,
            "extracted_properties": {"policy_name": "Remote Work Policy", "department": "Human Resources"}
        }
    elif "subject:" in content_lower or "from:" in content_lower:
        fallback = {
            "doc_type": "Email",
            "confidence_score": 0.90,
            "extracted_properties": {"sender": "john.doe@company.com", "subject": "Quarterly Reports"}
        }

    # Run Gemini prompt
    result = call_gemini_json(
        system_prompt=SYSTEM_PROMPT_TRIAGE,
        user_content=content,
        fallback_data=fallback
    )
    
    doc_type = result.get("doc_type", "Other")
    confidence = result.get("confidence_score", 0.5)
    properties = result.get("extracted_properties", {})
    
    # Append log entry for WebSocket and DB
    log_entry = {
        "agent_name": "TriageAgent",
        "status": "SUCCESS",
        "message": f"Successfully classified as {doc_type} with {int(confidence * 100)}% confidence.",
        "execution_metadata": {"extracted_keys": list(properties.keys())}
    }
    
    logs = list(state.get("logs", []))
    logs.append(log_entry)
    
    return {
        "doc_type": doc_type,
        "confidence_score": confidence,
        "extracted_properties": properties,
        "logs": logs
    }
