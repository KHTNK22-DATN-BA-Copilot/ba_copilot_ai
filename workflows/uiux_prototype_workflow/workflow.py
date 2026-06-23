"""
UI/UX Prototype Workflow for Phase 6 - UI/UX Design Phase
Generates interactive prototype specifications and user flow documentation
"""

from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional
from workflows.nodes import get_chat_history, get_context_node
from ..base.additional_rules import DIAGRAM_DOCUMENT_ADDITIONAL_RULES
from ..base.document_generator import generate_document
from ..base.state import BaseDocumentState


class UIUXPrototypeState(BaseDocumentState):
    pass

def generate_uiux_prototype(state: UIUXPrototypeState, config: Optional[dict] = None):
    """
    Generate interactive prototype specifications and user flow documentation
    """
    UIUX_PROTOTYPE_ADDITIONAL_RULES = DIAGRAM_DOCUMENT_ADDITIONAL_RULES + """
\n- Demonstrate Page structure (header, nav, main, sections, footer), Navigation flow and layout hierarchy, Interaction states (hover, focus, active), Responsive behavior (mobile, tablet, desktop)
- At least 3 interactive components (e.g., nav, cards, form, modal)
- Use semantic HTML and clear class naming
- Use CSS for layout, responsiveness (media queries), and interactions
- Follow modern UX principles (clarity, accessibility, spacing)
- HTML & CSS must be single-line strings
- Use single quotes for HTML attributes
- Do NOT include <style> tags
- No comments in CSS
- Include responsive + interaction states
- Escape quotes properly
"""
    return generate_document(
        state=state,
        config=config,
        role="Interaction Designer & Frontend Prototyper (HTML/CSS)",
        task="Create an interactive UIUX prototype",
        default_summary="UIUX Prototype",
        additional_rules=UIUX_PROTOTYPE_ADDITIONAL_RULES
    )

# Build workflow graph
workflow = StateGraph(UIUXPrototypeState)

# Add nodes
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_uiux_prototype", generate_uiux_prototype)

# Define edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_uiux_prototype")
workflow.add_edge("generate_uiux_prototype", END)

# Compile graph
uiux_prototype_graph = workflow.compile()
