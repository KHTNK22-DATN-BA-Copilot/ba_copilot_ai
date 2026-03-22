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
    You are a Database Architect.

    TASK:
    Generate a Low-Level Database Design (ERD) using Mermaid.

    PROJECT:
    {user_message}

    CONTEXT:
    {context_str}

    OUTPUT RULES (STRICT):
    - Return ONLY a Mermaid code block
    - Start with ```mermaid
    - End with ```
    - No explanation or extra text
    - Must be valid Mermaid erDiagram syntax

    ERD REQUIREMENTS:

    ENTITIES:
    - Define all tables with attributes
    - Include data types: uuid, string, int, decimal, boolean, timestamp
    - Mark:
    - PK (primary key)
    - FK (foreign key)
    - UNIQUE if applicable

    RELATIONSHIPS:
    - Define ALL relationships based on foreign keys
    - Use correct direction: parent ||--o{{ child
    - Use proper cardinality:
    - ||--o{{ : one-to-many
    - ||--|| : one-to-one
    - }}o--o{{ : many-to-many (via join table)
    - Every FK MUST have a relationship line

    NAMING:
    - Use uppercase for entity names
    - Use snake_case for columns
    - Use clear relationship labels (e.g., has, belongs_to, contains)

    QUALITY RULES:
    - No missing relationships
    - No incorrect directions
    - No orphan tables
    - Avoid redundant relationships
    - Ensure normalized structure (no duplicated data)

    EXAMPLE FORMAT:
    ```mermaid
    erDiagram
        CUSTOMER ||--o{{ ORDER : places

        CUSTOMER {{
            uuid id PK
            string email UNIQUE
            string name
            timestamp created_at
        }}

        ORDER {{
            uuid id PK
            uuid customer_id FK
            decimal total
            timestamp created_at
        }}
    """

    try:
        # Using Open Router (default)
        completion = model_client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL
        )
        raw_output = completion.choices[0].message.content or ""

        # Using Gemini 2.5 Flash lite
        # raw_output = model_client.gemini_completion(prompt)
        
        diagram = extract_mermaid(raw_output)
        if not diagram:
            logger.warning("No valid mermaid block found, returning raw output")
            diagram = raw_output
        return {
            "response": {
                "title": "Product Roadmap",
                "detail": diagram or "",
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        logger.exception(f"Error generating product roadmap: {e}")
    
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
