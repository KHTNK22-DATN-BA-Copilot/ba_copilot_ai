# workflows/risk_register_workflow/workflow.py

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


class RiskRegisterState(BaseDocumentState):
    pass


RISK_REGISTER_RULES = """
 ### RULES
- Output JSON ONLY (no markdown wrappers, no explanations)
- No extra keys, no missing keys
- Do NOT change section titles or order
- Escape \\n properly
- All values must be strings
"""


def generate_risk_register(
    state: RiskRegisterState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="Business Analyst (risk management)",
        task="""
Create a Risk Register document
for the provided project or business idea.
""",
        default_summary="Risk Register",
        additional_rules=RISK_REGISTER_RULES,
    )


workflow = StateGraph(RiskRegisterState)

workflow.add_node(
    "get_content_file",
    get_content_file,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_risk_register",
    generate_risk_register,
)

workflow.set_entry_point("get_content_file")

workflow.add_edge(
    "get_content_file",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_risk_register",
)

workflow.add_edge(
    "generate_risk_register",
    END,
)

risk_register_graph = workflow.compile()
