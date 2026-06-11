# workflows/cost_benefit_analysis_workflow/workflow.py

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


class CostBenefitAnalysisState(BaseDocumentState):
    pass


COST_BENEFIT_ANALYSIS_RULES = """
### RULES
- Return ONLY valid JSON (no markdown wrapper, no extra text)
- ALL values must be strings
- Escape \\n properly
- Do NOT return empty fields
- Use realistic numbers or reasonable estimates
- If data is missing, make assumptions and state them
- Keep content concise but complete
"""


def generate_cost_benefit_analysis(
    state: CostBenefitAnalysisState,
    config: Optional[dict] = None,
):
    return generate_document(
        state=state,
        config=config,
        role="Professional Business Analyst (Cost-Benefit Analysis)",
        task="""
Create a Cost-Benefit Analysis document
for the provided project or business idea.
""",
        default_summary="Cost Benefit Analysis",
        additional_rules=COST_BENEFIT_ANALYSIS_RULES,
    )


workflow = StateGraph(CostBenefitAnalysisState)

workflow.add_node(
    "get_context_node",
    get_context_node,
)

workflow.add_node(
    "get_chat_history",
    get_chat_history,
)

workflow.add_node(
    "generate_cost_benefit_analysis",
    generate_cost_benefit_analysis,
)

workflow.set_entry_point("get_context_node")

workflow.add_edge(
    "get_context_node",
    "get_chat_history",
)

workflow.add_edge(
    "get_chat_history",
    "generate_cost_benefit_analysis",
)

workflow.add_edge(
    "generate_cost_benefit_analysis",
    END,
)

cost_benefit_analysis_graph = workflow.compile()
