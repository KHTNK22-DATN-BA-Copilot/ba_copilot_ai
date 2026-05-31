# workflows/high_level_requirements_workflow/workflow.py

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


class HighLevelRequirementsState(BaseDocumentState):
    pass


HIGH_LEVEL_REQUIREMENTS_RULES = """
### REQUIREMENTS
Include:
- Functional requirements (categorized, unique IDs: FR-XXX)
- Non-functional requirements (measurable, IDs: NFR-XXX)
- Stakeholder needs
- Constraints, assumptions, dependencies
- Acceptance criteria (specific, measurable)

### RULES
- Use clear, structured Markdown
- Use IDs for requirements (FR-XXX, NFR-XXX)
- Include tables where appropriate
- Keep content concise but complete
"""


def generate_high_level_requirements(
    state: HighLevelRequirementsState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="Professional Business Analyst (Requirements)",
        task="""
Create a professional High-Level Requirements document
for the provided project or business idea.
""",
        default_summary="High-Level Requirements",
        additional_rules=HIGH_LEVEL_REQUIREMENTS_RULES,
    )


workflow = StateGraph(HighLevelRequirementsState)

workflow.add_node(
    "get_context_node",
    get_context_node,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_high_level_requirements",
    generate_high_level_requirements,
)

workflow.set_entry_point("get_context_node")

workflow.add_edge(
    "get_context_node",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_high_level_requirements",
)

workflow.add_edge(
    "generate_high_level_requirements",
    END,
)

high_level_requirements_graph = workflow.compile()
