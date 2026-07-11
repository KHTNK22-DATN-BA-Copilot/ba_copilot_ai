# workflows/lld_api_workflow/workflow.py

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
from utils.prompt_builder import build_document_prompt
from utils.default_document_format import DocumentFormat

logger = logging.getLogger(__name__)


class LLDAPIState(BaseDocumentState):
    pass


LLD_API_RULES = """
### RULES
- Use concise formatting
- Use clean and readable Markdown
- Include realistic request/response examples
- Do NOT leave any section empty
- Do NOT change section titles or order
"""


def generate_lld_api_specs(
    state: LLDAPIState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="API Architect (REST, OpenAPI-style)",
        task="""
Design a detailed Low-Level API Specification
for the provided project, platform, or system.
""",
        default_summary="LLD API",
        default_format=DocumentFormat.LLD_API,
        prompt_builder=build_document_prompt,
        additional_rules=LLD_API_RULES,
    )


workflow = StateGraph(LLDAPIState)

workflow.add_node(
    "get_context_node",
    get_context_node,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_lld_api",
    generate_lld_api_specs,
)

workflow.set_entry_point("get_context_node")

workflow.add_edge(
    "get_context_node",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_lld_api",
)

workflow.add_edge(
    "generate_lld_api",
    END,
)

lld_api_graph = workflow.compile()
