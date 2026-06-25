from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes.triage import triage_node
from app.agents.nodes.compliance import compliance_node
from app.agents.nodes.enrichment import enrichment_node
from app.agents.nodes.router import router_node

def create_swarm_graph() -> StateGraph:
    """
    Creates and links the LangGraph multi-agent swarm state graph.
    Flow: Triage -> Compliance Guardian -> Enrichment Analytics -> Action Router -> End
    """
    workflow = StateGraph(AgentState)
    
    # Register the nodes
    workflow.add_node("triage", triage_node)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("enrichment", enrichment_node)
    workflow.add_node("router", router_node)
    
    # Establish edges (triage -> compliance -> enrichment -> router -> END)
    workflow.set_entry_point("triage")
    workflow.add_edge("triage", "compliance")
    workflow.add_edge("compliance", "enrichment")
    workflow.add_edge("enrichment", "router")
    workflow.add_edge("router", END)
    
    return workflow.compile()

# Precompiled graph instance
swarm_graph = create_swarm_graph()
