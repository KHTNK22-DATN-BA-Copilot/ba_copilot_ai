# workflows/usecase_diagram_workflow/workflow.py

from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional
from workflows.nodes import get_chat_history, get_context_node
from ..base.additional_rules import DIAGRAM_DOCUMENT_ADDITIONAL_RULES
from ..base.document_generator import generate_document
from ..base.state import BaseDocumentState


class UsecaseDiagramState(BaseDocumentState):
    pass

def generate_usecase_diagram_description(state: UsecaseDiagramState, config: Optional[dict] = None):
    """Generate use-case diagram in markdown format using OpenRouter AI"""
    USECASE_DIAGRAM_ADDITIONAL_RULES = DIAGRAM_DOCUMENT_ADDITIONAL_RULES + """
\n- Use Mermaid flowchart (graph TD or TB), start the Mermaid content with `graph TD` or `graph TB`
- Include:
    - System boundary (labeled)
    - Actors (primary, secondary; e.g., User, Admin, External System)
    - Use cases (verb + noun naming)
    - Associations (actor ↔ use case)
- Relationships:
    - include
    - extend
    - generalization
- Group elements clearly (e.g., system boundary via subgraph)
- Ensure logical structure and readability
"""
    return generate_document(
        state=state,
        config=config,
        role="Expert UML Use Case Diagram Desinger (Mermaid)",
        task="Create UML Use Case Diagram",
        default_summary="Use Case Diagram",
        additional_rules=USECASE_DIAGRAM_ADDITIONAL_RULES
    )

# Build LangGraph pipeline for Use Case Diagram
workflow = StateGraph(UsecaseDiagramState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_usecase_diagram", generate_usecase_diagram_description)
# workflow.add_node("validate_diagram", validate_diagram)
# workflow.add_node("finalize_response", finalize_response)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_usecase_diagram")
# workflow.add_edge("generate_usecase_diagram", "validate_diagram")
# workflow.add_edge("validate_diagram", "finalize_response")
# workflow.add_edge("finalize_response", END)
workflow.add_edge("generate_usecase_diagram", END)

# Compile graph
usecase_diagram_graph = workflow.compile()
