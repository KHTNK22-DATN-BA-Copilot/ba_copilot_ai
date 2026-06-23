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
    UIUX_WIREFRAME_ADDITIONAL_RULES = DIAGRAM_DOCUMENT_ADDITIONAL_RULES + """
\n- Define layout structure using semantic HTML (header, nav, main, section, footer)
- Show layout hierarchy and content grouping
- Include navigation, hero, content sections, and at least 1 form
- Use grid/flex for layout
- Include responsive behavior (mobile breakpoint)
- Focus on structure, NOT visual styling
- No markdown, no explanations
- HTML & CSS MUST NOT be empty
- HTML & CSS must be single-line strings
- Use single quotes in HTML
- Do NOT include <style> tags
- No comments in CSS
- Include responsive layout (@media)
- Escape quotes properly
"""
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
