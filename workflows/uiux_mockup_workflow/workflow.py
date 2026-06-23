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
    UIUX_MOCKUP_ADDITIONAL_RULES = DIAGRAM_DOCUMENT_ADDITIONAL_RULES + """
\n- Clean, modern design with strong layout and typography
- Include Page structure (header, main, sections, footer), Visual hierarchy and spacing, UI components (buttons, cards, forms if relevant)
- Consistent styling and responsive-friendly layout
- Use semantic HTML and clear class naming
- Minimal, professional color palette
- HTML & CSS must be single-line strings
- Use single quotes for HTML attributes
- Do NOT include <style> tags
- No comments in CSS
- Escape quotes properly
- Ensure valid JSON (parsable)
"""
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
