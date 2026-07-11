# workflows/hld_arch_workflow/workflow.py
from langgraph.graph import StateGraph, END

import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
# from models.hld_arch import HLDArchOutput, HLDArchResponse
from typing import Optional
from workflows.nodes import get_chat_history, get_context_node
from ..base.document_generator import generate_document
from ..base.state import BaseDocumentState
from ..base.additional_rules import DIAGRAM_DOCUMENT_ADDITIONAL_RULES
from utils.prompt_builder import build_document_prompt
from utils.default_document_format import DocumentFormat


class HLDArchState(BaseDocumentState):
    pass


def generate_hld_arch_diagram(state: HLDArchState, config: Optional[dict] = None):
    """Generate High-Level Design Architecture Diagram in Mermaid format"""
    HLD_ARCH_ADDITIONAL_RULES = (
        DIAGRAM_DOCUMENT_ADDITIONAL_RULES
        + """
\n-Include:
    - System components (frontend, backend, database, services)
    - External systems (APIs, third-party)
    - Data flow (directional)
    - Layers (presentation, application, data)
    - Infrastructure (LB, cache, queues)
    - Security boundaries (auth, gateway, firewall)
- Mermaid flowchart, start the Mermaid content with `graph TD` or `graph TB`
- Subgraphs for architectural layers
- Clear labels and directional connections
- Consistent node naming
- Logical grouping of related services
- Readable and valid Mermaid structure
"""
    )
    return generate_document(
        state=state,
        config=config,
        role="Solution Architect specializing in HLD, Mermaid",
        task="Create a complete High-level System Architecture Diagram",
        default_summary="High-level System Architecture Diagram",
        default_format=DocumentFormat.HLD_ARCH,
        prompt_builder=build_document_prompt,
        additional_rules=HLD_ARCH_ADDITIONAL_RULES,
    )


# Build LangGraph pipeline for HLD Architecture
workflow = StateGraph(HLDArchState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_hld_arch", generate_hld_arch_diagram)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_hld_arch")
workflow.add_edge("generate_hld_arch", END)

# Compile graph
hld_arch_graph = workflow.compile()
