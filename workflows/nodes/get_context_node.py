# workflows/nodes/get_context_node.py
"""
Node to fetch RAG context using semantic search over indexed chunks.
"""

import os
import sys
from typing import Any, Dict, List
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.rag import retrieve_rag_context


async def get_context_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function to retrieve top-k RAG context for the current prompt.

    Args:
        state: Current workflow state containing user_message and storage_paths

    Returns:
        Updated state with extracted_text set to RAG context
    """
    query = state.get("user_message", "")
    storage_paths: List[str] = state.get("storage_paths", []) or []

    if not query or not storage_paths:
        state["extracted_text"] = ""
        return state

    try:
        context = retrieve_rag_context(query=query, storage_paths=storage_paths, top_k=5)
        state["extracted_text"] = context
    except Exception as e:
        print(f"Error retrieving RAG context: {e}")
        print(traceback.format_exc())
        state["extracted_text"] = ""

    return state
