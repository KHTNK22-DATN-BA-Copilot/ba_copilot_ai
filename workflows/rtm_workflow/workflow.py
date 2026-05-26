# workflows/rtm_workflow/workflow.py

from langgraph.graph import StateGraph, END

import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from typing import Optional

from workflows.nodes import (
    get_chat_history,
    get_content_file,
)

from ..base.state import BaseDocumentState

from ..base.document_generator import (
    generate_document,
)


class RTMState(BaseDocumentState):
    pass


RTM_RULES = """
### RULES
- Use concise bullet points (except tables)
- Do NOT leave any section empty
- Use clean and readable Markdown
- Keep content concise but complete
- Do NOT change section titles or order
"""


def generate_rtm(
    state: RTMState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="Business Analyst / QA Specialist (traceability, quality)",
        task="""
Create a Requirements Traceability Matrix (RTM)
for the provided project, platform, or system.
""",
        default_summary="RTM",
        additional_rules=RTM_RULES,
    )


workflow = StateGraph(RTMState)

workflow.add_node(
    "get_content_file",
    get_content_file,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_rtm",
    generate_rtm,
)

workflow.set_entry_point("get_content_file")

workflow.add_edge(
    "get_content_file",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_rtm",
)

workflow.add_edge(
    "generate_rtm",
    END,
)

rtm_graph = workflow.compile()
