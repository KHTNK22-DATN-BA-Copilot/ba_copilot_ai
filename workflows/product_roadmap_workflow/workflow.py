# workflows/product_roadmap_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional
from workflows.nodes import get_chat_history, get_context_node
from ..base.additional_rules import DIAGRAM_DOCUMENT_ADDITIONAL_RULES
from ..base.document_generator import generate_document
from ..base.state import BaseDocumentState
from utils.prompt_builder import build_document_prompt


class ProductRoadmapState(BaseDocumentState):
    pass

def generate_product_roadmap_diagram(state: ProductRoadmapState, config: Optional[dict] = None):
    """Generate product roadmap Gantt diagram using OpenRouter AI"""
    PRODUCT_ROADMAP_ADDITIONAL_RULES = DIAGRAM_DOCUMENT_ADDITIONAL_RULES + """
\n- Use Mermaid Gantt
- Include:
    - title
    - dateFormat YYYY-MM-DD with actual valid date from context or right now
    - sections: Planning, Design, Development, Testing, Deployment
    - tasks with:
        - start date + duration (e.g., 2024-01-01, 30d) OR
        - dependencies using "after"
- Timeline must span multiple months
- Use clear, realistic task names and sequencing
- Exactly one task per line (never place multiple tasks on the same line)
"""
    return generate_document(
        state=state,
        config=config,
        role="Expert Product Manager (Mermaid, Gantt)",
        task="Create a Product Roadmap",
        default_summary="Product Roadmap Diagram",
        prompt_builder=build_document_prompt,
        additional_rules=PRODUCT_ROADMAP_ADDITIONAL_RULES
    )

# Build LangGraph pipeline for Product Roadmap
workflow = StateGraph(ProductRoadmapState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate -> Validate -> Finalize
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_product_roadmap", generate_product_roadmap_diagram)
# workflow.add_node("validate_diagram", validate_diagram)
# workflow.add_node("finalize_response", finalize_response)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_product_roadmap")
# workflow.add_edge("generate_product_roadmap", "validate_diagram")
# workflow.add_edge("validate_diagram", "finalize_response")
# workflow.add_edge("finalize_response", END)
workflow.add_edge("generate_product_roadmap", END)

# Compile graph
product_roadmap_graph = workflow.compile()
