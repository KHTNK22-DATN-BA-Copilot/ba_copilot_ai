# workflows/nodes/get_context_node.py
"""
Node to fetch RAG context using semantic search over indexed chunks.
"""

import os
import sys
from typing import Any, Dict, List
import traceback
from sqlalchemy.exc import OperationalError, SQLAlchemyError

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from services.rag import retrieve_rag_context


async def get_context_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function to retrieve top-k RAG context for the current prompt.

    Args:
        state: Current workflow state containing user_message, project_id, and document_constraint

    Returns:
        Updated state with extracted_text set to RAG context
    """
    query = state.get("user_message", "")
    project_id = state.get("project_id")
    document_constraint: List[str] = state.get("document_constraint", []) or []

    print(
        f"Getting RAG context for query: '{query}' with constraints: {document_constraint} and project_id: {project_id}"
    )

    if not query and project_id is None and not document_constraint:
        state["extracted_text"] = ""
        return state

    try:
        context = retrieve_rag_context(
            query=query,
            project_id=project_id,
            document_constraint=document_constraint,
            top_k=5,
        )
        state["extracted_text"] = context
    except OperationalError as exc:
        print(f"RAG DB connection error: {exc}")
        print(traceback.format_exc())
        state["extracted_text"] = ""
    except SQLAlchemyError as exc:
        print(f"RAG DB SQLAlchemy error: {exc}")
        print(traceback.format_exc())
        state["extracted_text"] = ""
    except Exception as exc:
        print(f"RAG retrieval unexpected error: {exc}")
        print(traceback.format_exc())
        state["extracted_text"] = ""

    return state
