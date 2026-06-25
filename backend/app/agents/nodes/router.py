from app.agents.state import AgentState
from app.agents.prompts import SYSTEM_PROMPT_ROUTER
from app.agents.nodes import call_gemini_json

def router_node(state: AgentState) -> dict:
    """
    Agent C: Action/Router.
    Examines previous outcomes, decides on corporate action routes, and drafts responses.
    """
    doc_type = state.get("doc_type", "Other")
    compliance_status = state.get("compliance_status", "PASSED")
    risk_level = state.get("risk_level", "LOW")
    
    # Summarize state for the agent input
    agent_input = f"""
    Document Type: {doc_type}
    Compliance Status: {compliance_status}
    Risk Level: {risk_level}
    """
    
    # Prepare realistic fallback structure
    fallback = {
        "recommended_action": "Manual Review Required",
        "drafted_response": "The document has been routed for manual inspection by an administrator."
    }
    
    if compliance_status == "PASSED":
        if doc_type == "Invoice":
            fallback = {
                "recommended_action": "Route to Finance for Payment",
                "drafted_response": "Dear Vendor,\n\nWe have received and verified your invoice. It has been routed to our accounts team for payment processing.\n\nBest regards,\nAccounts Payable Team"
            }
        elif doc_type == "Contract":
            fallback = {
                "recommended_action": "Route to Legal Registry",
                "drafted_response": "MEMORANDUM\n\nSubject: Compliant Contract Registry Clearance\n\nThis contract has passed PII vetting and is cleared for archival in the Legal document repository."
            }
    elif compliance_status in ["WARNING", "VIOLATED"]:
        fallback = {
            "recommended_action": "Block and Escalate to Compliance Team",
            "drafted_response": f"ALERT: A document of type '{doc_type}' has triggered a compliance risk '{risk_level}'. Access has been restricted."
        }

    # Run Gemini prompt
    result = call_gemini_json(
        system_prompt=SYSTEM_PROMPT_ROUTER,
        user_content=agent_input,
        fallback_data=fallback
    )
    
    recommended_action = result.get("recommended_action", "Manual Review Required")
    drafted_response = result.get("drafted_response", "")
    
    # Append log entry for WebSocket and DB
    log_entry = {
        "agent_name": "ActionRouter",
        "status": "SUCCESS",
        "message": f"Formulated action: '{recommended_action}'. Automatically drafted response.",
        "execution_metadata": {"recommended_action": recommended_action}
    }
    
    logs = list(state.get("logs", []))
    logs.append(log_entry)
    
    return {
        "recommended_action": recommended_action,
        "drafted_response": drafted_response,
        "logs": logs
    }
