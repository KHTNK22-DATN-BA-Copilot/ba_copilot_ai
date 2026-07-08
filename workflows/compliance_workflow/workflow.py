# workflows/compliance_workflow/workflow.py

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


class ComplianceState(BaseDocumentState):
    pass


COMPLIANCE_RULES = """
### RULES
- Return ONLY valid JSON (no markdown wrapper, no extra text)
- Use clear, structured Markdown
- Keep content concise but complete
- Ensure JSON is parsable (escape \\n properly)
"""


def generate_compliance(
    state: ComplianceState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="Professional Business Analyst (Compliance)",
        task="""
Create a Compliance document
for the provided project or business idea.
""",
        default_summary="Compliance",
        prompt_builder=build_document_prompt,
        additional_rules=COMPLIANCE_RULES,
    )


workflow = StateGraph(ComplianceState)

workflow.add_node(
    "get_context_node",
    get_context_node,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_compliance",
    generate_compliance,
)

workflow.set_entry_point("get_context_node")

workflow.add_edge(
    "get_context_node",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_compliance",
)

workflow.add_edge(
    "generate_compliance",
    END,
)

compliance_graph = workflow.compile()
