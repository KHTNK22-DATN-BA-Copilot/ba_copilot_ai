# workflows/lld_pseudocode_workflow/workflow.py

from langgraph.graph import StateGraph, END

import logging

from typing import Optional

from workflows.nodes import (
    get_chat_history,
    get_context_node,
)

from ..base.state import BaseDocumentState

from ..base.document_generator import (
    generate_document,
)

logger = logging.getLogger(__name__)


class LLDPseudoState(BaseDocumentState):
    pass


LLD_PSEUDOCODE_RULES = """
### RULES
- Use concise bullet points (except pseudocode)
- Ensure clarity and correctness
- Do NOT change section titles or order
- Use clean, structured Markdown
"""


def generate_lld_pseudocode(
    state: LLDPseudoState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="Algorithm Designer (pseudocode, analysis)",
        task="""
Create a detailed Pseudocode Design document
for the provided algorithm, system, or feature.
""",
        default_summary="LLD Pseudo",
        additional_rules=LLD_PSEUDOCODE_RULES,
    )


workflow = StateGraph(LLDPseudoState)

workflow.add_node(
    "get_context_node",
    get_context_node,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_lld_pseudo",
    generate_lld_pseudocode,
)

workflow.set_entry_point("get_context_node")

workflow.add_edge(
    "get_context_node",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_lld_pseudo",
)

workflow.add_edge(
    "generate_lld_pseudo",
    END,
)

lld_pseudo_graph = workflow.compile()
