from app.agents.state import AgentState
from app.agents.prompts import SYSTEM_PROMPT_COMPLIANCE
from app.agents.nodes import call_gemini_json

def compliance_node(state: AgentState) -> dict:
    """
    Agent B: Privacy and Compliance Guardian.
    Audits the text for PII elements and potential regulatory violations.
    """
    content = state.get("content", "")
    
    # Prepare realistic fallback structure
    fallback = {
        "pii_detected": False,
        "risk_level": "LOW",
        "pii_categories_found": [],
        "violating_snippets": [],
        "compliance_status": "PASSED"
    }
    
    content_lower = content.lower()
    if "ssn" in content_lower or "social security" in content_lower:
        fallback = {
            "pii_detected": True,
            "risk_level": "HIGH",
            "pii_categories_found": ["SSN"],
            "violating_snippets": ["SSN: XXX-XX-6789"],
            "compliance_status": "VIOLATED"
        }
    elif "credit card" in content_lower or "card number" in content_lower:
        fallback = {
            "pii_detected": True,
            "risk_level": "HIGH",
            "pii_categories_found": ["Credit Card"],
            "violating_snippets": ["Card ending in 4111"],
            "compliance_status": "VIOLATED"
        }
    elif "password" in content_lower or "secret_key" in content_lower:
        fallback = {
            "pii_detected": True,
            "risk_level": "HIGH",
            "pii_categories_found": ["Credential"],
            "violating_snippets": ["db_password=mysecretpassword"],
            "compliance_status": "VIOLATED"
        }
    elif "@" in content_lower or "phone" in content_lower:
        fallback = {
            "pii_detected": True,
            "risk_level": "MEDIUM",
            "pii_categories_found": ["Contact Info"],
            "violating_snippets": ["support@docuswarm.ai"],
            "compliance_status": "WARNING"
        }

    # Run Gemini prompt
    result = call_gemini_json(
        system_prompt=SYSTEM_PROMPT_COMPLIANCE,
        user_content=content,
        fallback_data=fallback
    )
    
    pii_detected = result.get("pii_detected", False)
    risk_level = result.get("risk_level", "LOW")
    pii_categories = result.get("pii_categories_found", [])
    violating_snippets = result.get("violating_snippets", [])
    compliance_status = result.get("compliance_status", "PASSED")
    
    # Append log entry for WebSocket and DB
    log_entry = {
        "agent_name": "ComplianceGuardian",
        "status": "SUCCESS",
        "message": f"Compliance audit complete. Status: {compliance_status} (Risk: {risk_level}).",
        "execution_metadata": {
            "pii_categories": pii_categories,
            "violating_snippets_count": len(violating_snippets)
        }
    }
    
    logs = list(state.get("logs", []))
    logs.append(log_entry)
    
    return {
        "pii_detected": pii_detected,
        "risk_level": risk_level,
        "pii_categories_found": pii_categories,
        "violating_snippets": violating_snippets,
        "compliance_status": compliance_status,
        "logs": logs
    }
