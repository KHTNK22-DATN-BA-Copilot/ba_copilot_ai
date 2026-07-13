# workflows/requirements_management_plan_workflow/workflow.py

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
from utils.prompt_builder import build_document_prompt
from utils.default_document_format import DocumentFormat


class RequirementsManagementPlanState(BaseDocumentState):
    pass


REQUIREMENTS_MANAGEMENT_PLAN_RULES = """
### RULES
- Use concise bullet points
- Do NOT leave any section empty
- Use clear, structured Markdown
- Include tables where appropriate
- Do NOT change section titles or order
"""


def generate_requirements_management_plan(
    state: RequirementsManagementPlanState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="Business Analyst (requirements management)",
        task="""
Create a professional Requirements Management Plan
for the provided project or business idea.
""",
        default_summary="Requirements Management Plan",
        default_format=DocumentFormat.REQUIREMENTS_MANAGEMENT_PLAN,
        prompt_builder=build_document_prompt,
        additional_rules=REQUIREMENTS_MANAGEMENT_PLAN_RULES,
    )


workflow = StateGraph(RequirementsManagementPlanState)

workflow.add_node(
    "get_context_node",
    get_context_node,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_requirements_management_plan",
    generate_requirements_management_plan,
)

workflow.set_entry_point("get_context_node")

workflow.add_edge(
    "get_context_node",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_requirements_management_plan",
)

workflow.add_edge(
    "generate_requirements_management_plan",
    END,
)

requirements_management_plan_graph = workflow.compile()
