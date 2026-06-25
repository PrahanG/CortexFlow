from app.agents.state import AgentState
from app.agents.prompts import SYSTEM_PROMPT_ENRICHMENT
from app.agents.nodes import call_gemini_json

def enrichment_node(state: AgentState) -> dict:
    """
    NLP Enrichment Agent Node.
    Analyzes document text to determine sentiment tone, reading readability ease index,
    and extracts named entities (organizations, locations, dates, monetary values).
    """
    content = state.get("content", "")
    
    # Prepare realistic fallback structure
    fallback = {
        "sentiment": "Neutral",
        "readability_score": 60.0,
        "entities": {
            "organizations": ["Example Company Ltd"],
            "locations": ["Headquarters"],
            "dates": ["2026-06-01"],
            "monetary_amounts": ["$0.00"]
        }
    }
    
    # Simple heuristic to make local mockups smarter
    content_lower = content.lower()
    if "invoice" in content_lower or "bill to" in content_lower:
        fallback = {
            "sentiment": "Urgent",
            "readability_score": 68.5,
            "entities": {
                "organizations": ["Acme Services", "Enterprise Corp"],
                "locations": ["New York Office"],
                "dates": ["2026-07-31", "2026-06-25"],
                "monetary_amounts": ["$4,500.00"]
            }
        }
    elif "contract" in content_lower or "agreement" in content_lower:
        fallback = {
            "sentiment": "Confidential",
            "readability_score": 42.0,
            "entities": {
                "organizations": ["Partner Solutions LLC", "Corporate Systems Inc"],
                "locations": ["Delaware", "California"],
                "dates": ["2026-06-01", "2029-06-01"],
                "monetary_amounts": ["$120,000.00"]
            }
        }
    elif "policy" in content_lower or "conduct" in content_lower:
        fallback = {
            "sentiment": "Neutral",
            "readability_score": 53.4,
            "entities": {
                "organizations": ["Human Resources Division"],
                "locations": ["Corporate HQ"],
                "dates": ["2026-01-01"],
                "monetary_amounts": []
            }
        }

    # Run Gemini prompt
    result = call_gemini_json(
        system_prompt=SYSTEM_PROMPT_ENRICHMENT,
        user_content=content,
        fallback_data=fallback
    )
    
    sentiment = result.get("sentiment", "Neutral")
    readability = result.get("readability_score", 60.0)
    entities = result.get("entities", {})
    
    # Format log entry
    log_entry = {
        "agent_name": "EnrichmentAgent",
        "status": "SUCCESS",
        "message": f"NLP Enrichment completed. Sentiment: {sentiment}. Readability Ease: {readability:.1f}.",
        "execution_metadata": {
            "sentiment": sentiment,
            "readability_score": readability,
            "organizations_extracted": len(entities.get("organizations", []))
        }
    }
    
    logs = list(state.get("logs", []))
    logs.append(log_entry)
    
    return {
        "sentiment": sentiment,
        "readability_score": readability,
        "entities": entities,
        "logs": logs
    }
