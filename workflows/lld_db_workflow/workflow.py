"""
LLD Database Schema Workflow
Generates database Entity-Relationship Diagrams (ERD) using Mermaid.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List
import logging
import re
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
# from models.lld_db import LLDDBResponse, LLDDBOutput
from ..utils import extractor

logger = logging.getLogger(__name__)

class LLDDBState(TypedDict):
    """State for LLD Database Schema workflow"""
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List[str]]
    extracted_text: Optional[str]
    chat_context: Optional[str]
    
def extract_mermaid(text: str) -> str:
    match = re.search(r"```mermaid\s*(.*?)```", text, re.DOTALL)
    return match.group(0) if match else ""

def generate_lld_db_schema(state: LLDDBState):
    """
    Generate database ERD schema using LLM.
    Creates Entity-Relationship Diagrams with tables, columns, relationships.
    """
    model_client = get_model_client()

    # Build comprehensive prompt with context
    user_message = state.get('user_message', '')
    extracted_text = state.get('extracted_text', '')
    chat_context = state.get('chat_context', '')

    context_parts = []
    if chat_context:
        context_parts.append(f"Context from previous conversation:\n{chat_context}\n")
    if extracted_text:
        context_parts.append(f"Extracted content from uploaded files:\n{extracted_text}\n")

    context_str = "\n".join(context_parts)

    prompt = f"""
    {context_str}

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
    "content": "Mermaid ERD starting with 'erDiagram' (no backticks, use \\n for newlines)",
    "summary": "One-line concise description of the database design"
    }}

    ### RULES
    - Do NOT include ``` or markdown wrappers
    - Escape \\n properly
    - No extra keys, no extra text
    - Must be valid JSON (parsable)
    - Use valid Mermaid syntax only
    """

    try:
        # Use OpenRouter (default)
        # completion = model_client.chat_completion(
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": prompt
        #         }
        #     ],
        #     model=MODEL
        # )
        # raw_output = completion.choices[0].message.content

        # Use Gemini 2.5 Flash Lite
        raw_output = model_client.gemini_completion(prompt)

        json_data = extractor.extract_json(raw_output)
        summary = "LLD DB"
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "LLD DB")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        logger.exception(f"Error generating LLD DB: {e}")
    
# Build LangGraph pipeline for LLD Database Schema
workflow = StateGraph(LLDDBState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_lld_db", generate_lld_db_schema)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_lld_db")
workflow.add_edge("generate_lld_db", END)

# Compile graph
lld_db_graph = workflow.compile()
