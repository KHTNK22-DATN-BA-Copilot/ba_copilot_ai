# workflows/activity_diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional
from workflows.nodes import get_context_node, get_chat_history
from ..base.state import BaseDocumentState
from ..base.document_generator import generate_document
from ..base.additional_rules import DIAGRAM_DOCUMENT_ADDITIONAL_RULES
from utils.prompt_builder import build_document_prompt


class ActivityDiagramState(BaseDocumentState):
    pass

def generate_activity_diagram_description(state: ActivityDiagramState, config: Optional[dict] = None):
    """Generate activity diagram in markdown format using OpenRouter AI"""
    ACTIVITY_DIAGRAM_ADDTIONAL_RULES = DIAGRAM_DOCUMENT_ADDITIONAL_RULES + """
\n- Include: start/end, activities (verb + object), decisions (labeled), merges, flows
- Add swimlanes and parallel flows if applicable
- Ensure clear, logical structure
- Mermaid syntax must be valid
"""
    return generate_document(
        state=state,
        config=config,
        role="Expert UML Activity Diagram designer (Mermaid)",
        task="Create a UML Activity Diagram",
        default_summary="Actitivy Diagram",
        prompt_builder=build_document_prompt,
        additional_rules=ACTIVITY_DIAGRAM_ADDTIONAL_RULES
    )

workflow = StateGraph(ActivityDiagramState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_activity_diagram", generate_activity_diagram_description)
# workflow.add_node("validate_diagram", validate_diagram)
# workflow.add_node("finalize_response", finalize_response)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_activity_diagram")
workflow.add_edge("generate_activity_diagram", END)

# Compile graph
activity_diagram_graph = workflow.compile()
