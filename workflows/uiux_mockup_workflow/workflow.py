"""
UI/UX Mockup Workflow for Phase 6 - UI/UX Design Phase
Generates high-fidelity UI mockups with design specifications
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


class UIUXMockupState(BaseDocumentState):
    pass

def generate_uiux_mockup(state: UIUXMockupState, config: Optional[dict] = None):
    """
    Generate high-fidelity UI/UX mockup with design specifications
    """
    UIUX_MOCKUP_ADDITIONAL_RULES = (
        DIAGRAM_DOCUMENT_ADDITIONAL_RULES
        + """
\n- Generate the mockup as HTML and CSS only.
- The JSON `content` field MUST be an object with exactly two fields: `html` and `css`.
- Put the complete HTML document in `html` and all styles in `css`.
- Do not include any other fields inside `content`.
- Create a clean, modern, production-quality UI.
- Include a complete page structure (`header`, `main`, `section`, `footer`).
- Demonstrate strong visual hierarchy, spacing, typography, and alignment.
- Include realistic UI components (buttons, cards, forms, navigation, etc.) where appropriate.
- Use a consistent design system with a minimal, professional color palette.
- Use semantic HTML and meaningful class names.
- Implement responsive layouts and interaction states (`:hover`, `:focus`, `:active`) where appropriate.
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
        role="Visual Designer & Frontend Engineer (HTML/CSS mockups)",
        task="Create a UIUX mockup",
        default_summary="UIUX Mockup",
        additional_rules=UIUX_MOCKUP_ADDITIONAL_RULES
    )

# Build workflow graph
workflow = StateGraph(UIUXMockupState)

# Add nodes
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_uiux_mockup", generate_uiux_mockup)

# Define edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_uiux_mockup")
workflow.add_edge("generate_uiux_mockup", END)

# Compile graph
uiux_mockup_graph = workflow.compile()
