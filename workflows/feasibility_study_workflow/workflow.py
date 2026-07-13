# workflows/feasibility_study_workflow/workflow.py

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


class FeasibilityStudyState(BaseDocumentState):
    pass


FEASIBILITY_STUDY_RULES = """
### RULES
- Return ONLY valid JSON (no markdown wrapper, no extra text)
- Use clear, structured Markdown
- Keep content concise but complete
- Include key assumptions where relevant
- Ensure JSON is parsable (escape \\n properly)
"""


def generate_feasibility_study(
    state: FeasibilityStudyState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="Professional Business Analyst (Feasibility Study)",
        task="""
Create a Feasibility Study document
for the provided project or business idea.
""",
        default_summary="Feasibility Study",
        default_format=DocumentFormat.FEASIBILITY_STUDY,
        prompt_builder=build_document_prompt,
        additional_rules=FEASIBILITY_STUDY_RULES,
    )


workflow = StateGraph(FeasibilityStudyState)

workflow.add_node(
    "get_context_node",
    get_context_node,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_feasibility_study",
    generate_feasibility_study,
)

workflow.set_entry_point("get_context_node")

workflow.add_edge(
    "get_context_node",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_feasibility_study",
)

workflow.add_edge(
    "generate_feasibility_study",
    END,
)

feasibility_study_graph = workflow.compile()
