# workflows/business_case_workflow/workflow.py

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


class BusinessCaseState(BaseDocumentState):
    pass


BUSINESS_CASE_RULES = """
### RULES
- Use well-structured Markdown
- Include tables where specified
- Keep content concise but complete
- Do NOT leave important sections empty
"""


def generate_business_case(
    state: BusinessCaseState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="Professional Business Analyst",
        task="""
Create a complete Business Case document
for the provided project or business idea.
""",
        default_summary="Business Case",
        additional_rules=BUSINESS_CASE_RULES,
    )


workflow = StateGraph(BusinessCaseState)

workflow.add_node(
    "get_context_node",
    get_context_node,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_business_case",
    generate_business_case,
)

workflow.set_entry_point("get_context_node")

workflow.add_edge(
    "get_context_node",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_business_case",
)

workflow.add_edge(
    "generate_business_case",
    END,
)

business_case_graph = workflow.compile()
