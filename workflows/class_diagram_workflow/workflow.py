# workflows/class_diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional
from workflows.nodes import get_chat_history, get_context_node

from workflows.nodes import get_chat_history, get_context_node
from ..base.state import BaseDocumentState
from ..base.document_generator import (
    generate_document,
)
from ..base.additional_rules import DIAGRAM_DOCUMENT_ADDITIONAL_RULES
from utils.prompt_builder import build_document_prompt


class ClassDiagramState(BaseDocumentState):
    pass

def generate_class_diagram_description(state: ClassDiagramState, config: Optional[dict] = None):
    """Generate class diagram in markdown format using OpenRouter AI"""
    CLASS_DIAGRAM_ADDITIONAL_RULES = DIAGRAM_DOCUMENT_ADDITIONAL_RULES + """
\n- Classes: attributes (+/-/#, name, type) and methods (params, return, visibility)
- Relationships: association, aggregation, composition, inheritance, dependency
- Include multiplicity where relevant
- Use abstract classes/interfaces if needed
- Apply design patterns if appropriate
- Ensure clear, logical structure and valid Mermaid syntax
"""
    return generate_document(
        state=state,
        config=config,
        role="Expert UML Class Diagram designer (Mermaid)",
        task="Create a professional Class Diagram",
        default_summary="Class Diagram",
        prompt_builder=build_document_prompt,
        additional_rules=CLASS_DIAGRAM_ADDITIONAL_RULES
    )

# Build LangGraph pipeline for Class Diagram
workflow = StateGraph(ClassDiagramState)

# Add nodes in sequence
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_class_diagram", generate_class_diagram_description)
# workflow.add_node("validate_diagram", validate_diagram)
# workflow.add_node("finalize_response", finalize_response)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_class_diagram")
# workflow.add_edge("generate_class_diagram", "validate_diagram")
# workflow.add_edge("validate_diagram", "finalize_response")
# workflow.add_edge("finalize_response", END)
workflow.add_edge("generate_class_diagram", END)

# Compile graph
class_diagram_graph = workflow.compile()
