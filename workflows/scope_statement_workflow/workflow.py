# workflows/scope_statement_workflow/workflow.py

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


class ScopeStatementState(BaseDocumentState):
    pass


SCOPE_STATEMENT_RULES = """
### RULES
- Use concise bullet points (except tables)
- Do NOT leave any section empty
- Use clear, structured Markdown
- Include tables where specified
- Do NOT change section titles or order
"""


def generate_scope_statement(
    state: ScopeStatementState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="Business Analyst (scope definition, stakeholder alignment)",
        task="""
Create a professional Project Scope Statement
for the provided project or business idea.
""",
        default_summary="Scope Statement",
        additional_rules=SCOPE_STATEMENT_RULES,
    )


workflow = StateGraph(ScopeStatementState)

workflow.add_node(
    "get_content_file",
    get_content_file,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_scope_statement",
    generate_scope_statement,
)

workflow.set_entry_point("get_content_file")

workflow.add_edge(
    "get_content_file",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_scope_statement",
)

workflow.add_edge(
    "generate_scope_statement",
    END,
)

scope_statement_graph = workflow.compile()
