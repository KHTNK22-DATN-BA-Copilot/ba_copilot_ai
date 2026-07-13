from langgraph.graph import StateGraph, END
from typing import Optional
from workflows.nodes import get_chat_history, get_context_node
from ..base.additional_rules import DIAGRAM_DOCUMENT_ADDITIONAL_RULES
from ..base.document_generator import generate_document
from ..base.state import BaseDocumentState
from utils.prompt_builder import build_document_prompt
from utils.default_document_format import DocumentFormat


class LLDArchState(BaseDocumentState):
    pass


def generate_lld_arch_diagram(state: LLDArchState, config: Optional[dict] = None):
    """
    Generate detailed low-level architecture diagram using LLM.
    Creates component diagrams, deployment diagrams, or detailed system architecture.
    """
    LLD_ARCHITECTURE_ADITIONAL_RULES = (
        DIAGRAM_DOCUMENT_ADDITIONAL_RULES
        + """
\n- Include:
    - Components (services, modules, interfaces)
    - Internal structure and dependencies
    - Deployment elements (nodes, containers, network)
    - Data flow (directional)
    - Layers (presentation, application, data)
- Use subgraphs for layers, subsystems, or deployment zones
- Clearly label all nodes and connections
- Choose appropriate style (component, deployment, or hybrid)
- Ensure logical structure and readability
- ALWAYS start the Mermaid content with `graph TD` or `graph TB`
- The `content` field MUST contain a complete Mermaid markdown block"""
    )
    return generate_document(
        state=state,
        config=config,
        role="Expert Software Architect (Low-level Design, Mermaid)",
        task="Create a Low-level Architecture Design Architecture Diagram",
        default_summary="Low-level Architecture Design Diagram",
        default_format=DocumentFormat.LLD_ARCH,
        prompt_builder=build_document_prompt,
        additional_rules=LLD_ARCHITECTURE_ADITIONAL_RULES,
    )


# Build LangGraph pipeline for LLD Architecture
workflow = StateGraph(LLDArchState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_lld_arch", generate_lld_arch_diagram)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_lld_arch")
workflow.add_edge("generate_lld_arch", END)

# Compile graph
lld_arch_graph = workflow.compile()
