# workflows/srs_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional
from workflows.nodes import get_chat_history, get_context_node
from ..base.additional_rules import TEXT_DOCUMENT_ADDITONAL_RULES
from ..base.document_generator import generate_document
from ..base.state import BaseDocumentState
from utils.prompt_builder import build_document_prompt
from utils.default_document_format import DocumentFormat

class SRSState(BaseDocumentState):
    pass

def generate_srs(state: SRSState, config: Optional[dict] = None):
    """Generate SRS document using OpenRouter AI"""
    return generate_document(
        state=state,
        config=config,
        role="Business Analyst",
        task="Create a Software Requirements Specification (SRS)",
        default_summary="Software Requirements Specification",
        default_format=DocumentFormat.SRS,
        prompt_builder=build_document_prompt,
        additional_rules=TEXT_DOCUMENT_ADDITONAL_RULES
    )

# Build LangGraph pipeline for SRS
workflow = StateGraph(SRSState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_srs", generate_srs)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_srs")
workflow.add_edge("generate_srs", END)

# Compile graph
srs_graph = workflow.compile()
