"""
LLD Database Schema Workflow
Generates database Entity-Relationship Diagrams (ERD) using Mermaid.
"""

from langgraph.graph import StateGraph, END
from typing import Optional
from workflows.nodes import get_chat_history, get_context_node
from ..base.additional_rules import DIAGRAM_DOCUMENT_ADDITIONAL_RULES
from ..base.document_generator import generate_document
from ..base.state import BaseDocumentState
from utils.prompt_builder import build_document_prompt
from utils.default_document_format import DocumentFormat


class LLDDBState(BaseDocumentState):
    pass


def generate_lld_db_schema(state: LLDDBState, config: Optional[dict] = None):
    """
    Generate database ERD schema using LLM.
    Creates Entity-Relationship Diagrams with tables, columns, relationships.
    """
    LLD_DB_ADITIONAL_RULES = (
        DIAGRAM_DOCUMENT_ADDITIONAL_RULES
        + """
\n- Use Mermaid erDiagram
- Tables with attributes (name, type)
- Types: uuid, string, int, decimal, boolean, timestamp
- Mark PK, FK, UNIQUE where applicable
- Define ALL relationships from foreign keys
- Use correct cardinality:
    - ||--o{{ : one-to-many
    - ||--|| : one-to-one
    - }}o--o{{ : many-to-many (via join table)
- Every FK MUST have a relationship
- Use clear labels (e.g., has, belongs_to)
- UPPERCASE table names
- snake_case columns
- No missing or incorrect relationships
- No orphan tables
- Avoid redundancy, ensure normalized design
"""
    )

    return generate_document(
        state=state,
        config=config,
        role="Database Architect (ERD, Mermaid)",
        task="Create a Low-Level Database Design (ERD)",
        default_summary="Low-level Database Design",
        default_format=DocumentFormat.LLD_DB,
        prompt_builder=build_document_prompt,
        additional_rules=LLD_DB_ADITIONAL_RULES,
    )


# Build LangGraph pipeline for LLD Database Schema
workflow = StateGraph(LLDDBState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_lld_db", generate_lld_db_schema)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_lld_db")
workflow.add_edge("generate_lld_db", END)

# Compile graph
lld_db_graph = workflow.compile()
