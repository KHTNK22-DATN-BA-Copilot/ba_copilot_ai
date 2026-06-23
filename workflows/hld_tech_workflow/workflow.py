# workflows/hld_tech_workflow/workflow.py

from langgraph.graph import StateGraph, END

import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from typing import Optional

from workflows.nodes import (
    get_chat_history,
    get_context_node,
)

from ..base.state import BaseDocumentState

from ..base.document_generator import (
    generate_document,
)


class HLDTechState(BaseDocumentState):
    pass


HLD_TECH_RULES = """
### RULES
- Use concise bullet points
- Keep content concise but complete
- Do NOT change section titles or order
- Use clean Markdown formatting
"""


def generate_hld_tech(
    state: HLDTechState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="Senior Technical Architect (tech stack selection for scalable, maintainable systems)",
        task="""
Design a Technology Stack Selection document
for the provided project, system, or platform.
""",
        default_summary="HLD Tech",
        additional_rules=HLD_TECH_RULES,
    )


workflow = StateGraph(HLDTechState)

workflow.add_node(
    "get_context_node",
    get_context_node,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_hld_tech",
    generate_hld_tech,
)

workflow.set_entry_point("get_context_node")

workflow.add_edge(
    "get_context_node",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_hld_tech",
)

workflow.add_edge(
    "generate_hld_tech",
    END,
)

hld_tech_graph = workflow.compile()
