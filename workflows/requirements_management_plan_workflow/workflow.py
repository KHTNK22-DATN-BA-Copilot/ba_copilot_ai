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
    get_content_file,
)

from ..base.state import BaseDocumentState

from ..base.document_generator import (
    generate_document,
)


class RequirementsManagementPlanState(BaseDocumentState):
    pass


REQUIREMENTS_MANAGEMENT_PLAN_RULES = """
### REQUIREMENTS
The generated document must include:

# Requirements Management Plan - <Project Name>

## 1. Introduction
## 2. Requirements Management Approach
## 3. Elicitation
## 4. Analysis (MoSCoW)
## 5. Documentation
## 6. Validation
## 7. Traceability
- Include a traceability table

## 8. Change Management
## 9. Communication Plan
- Include a table

## 10. Roles & Responsibilities
## 11. Tools
## 12. Metrics
## 13. Quality Assurance
## 14. Training
## 15. Appendices
## 16. Approval

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
        additional_rules=REQUIREMENTS_MANAGEMENT_PLAN_RULES,
    )


workflow = StateGraph(RequirementsManagementPlanState)

workflow.add_node(
    "get_content_file",
    get_content_file,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_requirements_management_plan",
    generate_requirements_management_plan,
)

workflow.set_entry_point("get_content_file")

workflow.add_edge(
    "get_content_file",
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
