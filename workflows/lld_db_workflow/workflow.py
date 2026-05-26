"""
LLD Database Schema Workflow
Generates database Entity-Relationship Diagrams (ERD) using Mermaid.
"""

from langgraph.graph import StateGraph, END
from typing import Optional, List
import logging
import re
from workflows.nodes import get_chat_history, get_context_node
from connect_model import get_model_client, set_request_model_config, reset_request_model_config, MODEL
from utils import extractor
from response import success_response, error_response
from models import LLDDBState

logger = logging.getLogger(__name__)

def extract_mermaid(text: str) -> str:
    match = re.search(r"```mermaid\s*(.*?)```", text, re.DOTALL)
    return match.group(0) if match else ""

def generate_lld_db_schema(state: LLDDBState, config: Optional[dict] = None):
    """
    Generate database ERD schema using LLM.
    Creates Entity-Relationship Diagrams with tables, columns, relationships.
    """
    model_client = get_model_client()
    cfg = (config or {}).get("configurable", {})
    token = set_request_model_config(
        provider=cfg.get("provider"),
        model_name=cfg.get("model_name"),
        api_key=cfg.get("api_key"),
    )

    # Build system prompt
    user_message = state.get('user_message', '')
    extracted_text = state.get('extracted_text', '')
    chat_context = state.get('chat_context') or []
    prompt = f"""
    ### ROLE
    Database Architect (ERD, Mermaid).

    ### TASK
    Create a Low-Level Database Design (ERD) for: {user_message}

    ### REQUIREMENTS
    - Use Mermaid erDiagram
    - Entities:
    - Tables with attributes (name, type)
    - Types: uuid, string, int, decimal, boolean, timestamp
    - Mark PK, FK, UNIQUE where applicable
    - Relationships:
    - Define ALL relationships from foreign keys
    - Use correct cardinality:
        - ||--o{{ : one-to-many
        - ||--|| : one-to-one
        - }}o--o{{ : many-to-many (via join table)
    - Every FK MUST have a relationship
    - Use clear labels (e.g., has, belongs_to)
    - Naming:
    - UPPERCASE table names
    - snake_case columns
    - Quality:
    - No missing or incorrect relationships
    - No orphan tables
    - Avoid redundancy, ensure normalized design

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Mermaid ERD starting with 'erDiagram' (with backticks, use \\n for newlines)",
    "summary": "One-line concise description of the database design"
    }}

    ### RULES
    - Do include ``` as markdown wrappers
    - Escape \\n properly
    - No extra keys, no extra text
    - Must be valid JSON (parsable)
    - Use valid Mermaid syntax only
    """

    messages: List[dict] = [
        {"role": "system", "content": prompt},
        *chat_context,
    ]
    if extracted_text:
        messages.append({"role": "assistant", "content": extracted_text})
    messages.append({"role": "user", "content": user_message})

    try:
        response = model_client.chat_completion(
            messages=messages,
            model=cfg.get("model_name") or MODEL,
        )
        raw_output = response.choices[0].message.content or ""

        json_data = extractor.extract_json(raw_output)
        summary = "LLD DB"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "LLD DB")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": success_response(summary, content)
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        logger.exception(f"Error generating LLD DB: {e}")
        return {
            "response": error_response("LLD DB", f"Error generating LLD DB: {e}")
        } # pyright: ignore[reportReturnType]
    finally:
        reset_request_model_config(token)
    
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
