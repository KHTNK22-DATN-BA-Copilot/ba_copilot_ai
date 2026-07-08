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


class StakeholderRegisterState(BaseDocumentState):
    pass


def generate_stakeholder_register(
    state: StakeholderRegisterState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="Business Analyst (stakeholder management, communication)",
        task="""
Create a professional Stakeholder Register document
for the provided project or business idea
""",
        default_summary="Stakeholder Register",
        prompt_builder=build_document_prompt,
    )


workflow = StateGraph(StakeholderRegisterState)

workflow.add_node(
    "get_context_node",
    get_context_node,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_stakeholder_register",
    generate_stakeholder_register,
)

workflow.set_entry_point("get_context_node")

workflow.add_edge(
    "get_context_node",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_stakeholder_register",
)

workflow.add_edge(
    "generate_stakeholder_register",
    END,
)

stakeholder_register_graph = workflow.compile()
