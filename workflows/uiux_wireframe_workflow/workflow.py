"""
UI/UX Wireframe Workflow for Phase 6 - UI/UX Design Phase
Generates UI wireframes with layout and component specifications
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


class UIUXWireframeState(BaseDocumentState):
    pass

def generate_uiux_wireframe(state: UIUXWireframeState, config: Optional[dict] = None):
    """
    Generate UI/UX wireframe with layout and component specifications
    """
    UIUX_WIREFRAME_ADDITIONAL_RULES = (
        DIAGRAM_DOCUMENT_ADDITIONAL_RULES
        + """
\n- Generate the wireframe as HTML and CSS only.
- The JSON `content` field MUST be an object with exactly two fields: `html` and `css`.
- Put the complete HTML document in `html` and all styles in `css`.
- Do not include any other fields inside `content`.
- Define the layout using semantic HTML (`header`, `nav`, `main`, `section`, `footer`).
- Show clear layout hierarchy and content grouping.
- Include navigation, a hero section, content sections, and at least one form.
- Use CSS Grid and/or Flexbox for layout.
- Include responsive behavior with at least one `@media` breakpoint.
- Focus on structure and layout rather than visual styling.
- Use semantic HTML and meaningful class names.
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
        role="UX/UI Wireframe Designer (HTML/CSS)",
        task="Create UI Wireframe",
        default_summary="UIUX Wireframe",
        additional_rules=UIUX_WIREFRAME_ADDITIONAL_RULES
    )

# Build workflow graph
workflow = StateGraph(UIUXWireframeState)

# Add nodes
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_uiux_wireframe", generate_uiux_wireframe)

# Define edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_uiux_wireframe")
workflow.add_edge("generate_uiux_wireframe", END)

# Compile graph
uiux_wireframe_graph = workflow.compile()
