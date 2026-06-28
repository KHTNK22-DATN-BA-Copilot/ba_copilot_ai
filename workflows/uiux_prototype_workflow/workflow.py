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
    UIUX_PROTOTYPE_ADDITIONAL_RULES = (
        DIAGRAM_DOCUMENT_ADDITIONAL_RULES
        + """
\n- Generate the prototype as HTML and CSS only.
- The JSON `content` field MUST be an object with exactly two fields: `html` and `css`.
- Put the complete HTML document in `html` and all styles in `css`.
- Do not include any other fields inside `content`.
- Create a functional, high-fidelity interactive prototype.
- Demonstrate a complete page structure (`header`, `nav`, `main`, `section`, `footer`), navigation flow, and layout hierarchy.
- Include at least three interactive components (e.g., navigation, cards, forms, modal, tabs, accordion, dropdown).
- Implement interaction states (`:hover`, `:focus`, `:active`) and responsive layouts for mobile, tablet, and desktop.
- Use semantic HTML and meaningful class names.
- Use CSS for layout, responsiveness (media queries), transitions, and visual interactions.
- Follow modern UX principles, including accessibility, clarity, spacing, and visual consistency.
- HTML and CSS must each be returned as a single string.
- Use single quotes for HTML attributes.
- Do not embed CSS inside `<style>` tags.
- Do not include JavaScript.
- Do not include comments in HTML or CSS.
"""
    )
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
