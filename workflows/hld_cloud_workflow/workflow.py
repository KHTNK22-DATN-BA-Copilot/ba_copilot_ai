# workflows/hld_cloud_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from typing import Optional
from workflows.nodes import get_chat_history, get_context_node
from ..base.document_generator import generate_document
from ..base.state import BaseDocumentState
from ..base.additional_rules import TEXT_DOCUMENT_ADDITONAL_RULES
from utils.prompt_builder import build_document_prompt
from utils.default_document_format import DocumentFormat


class HLDCloudState(BaseDocumentState):
    pass


def generate_hld_cloud(state: HLDCloudState, config: Optional[dict] = None):
    """Generate Cloud Infrastructure Setup document"""
    return generate_document(
        state=state,
        config=config,
        role="Expert Cloud Architecture (scalable, secure, cost-optimized)",
        task="Design a Cloud Infrastructure Setup",
        default_summary="Cloud Infrastructure Setup",
        default_format=DocumentFormat.HLD_CLOUD,
        prompt_builder=build_document_prompt,
        additional_rules=TEXT_DOCUMENT_ADDITONAL_RULES,
    )


# Build LangGraph pipeline for Cloud Infrastructure Setup
workflow = StateGraph(HLDCloudState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_hld_cloud", generate_hld_cloud)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_hld_cloud")
workflow.add_edge("generate_hld_cloud", END)

# Compile graph
hld_cloud_graph = workflow.compile()
