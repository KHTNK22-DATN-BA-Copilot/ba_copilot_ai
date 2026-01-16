"""
LLD Database Schema Workflow
Generates database Entity-Relationship Diagrams (ERD) using Mermaid.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List
import json
import logging
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from models.lld_db import LLDDBResponse, LLDDBOutput

logger = logging.getLogger(__name__)

class LLDDBState(TypedDict):
    """State for LLD Database Schema workflow"""
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List[str]]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_lld_db_schema(state: LLDDBState) -> LLDDBState:
    """
    Generate database ERD schema using LLM.
    Creates Entity-Relationship Diagrams with tables, columns, relationships.
    """
    try:
        model_client = get_model_client()
        
        # Extract context
        user_message = state.get('user_message', '')
        extracted_text = state.get('extracted_text', '')
        chat_context = state.get('chat_context', '')
        
        # Build context string
        context_str = ""
        if chat_context:
            context_str += f"Context from previous conversation:\n{chat_context}\n\n"
        if extracted_text:
            context_str += f"Extracted content from uploaded files:\n{extracted_text}\n\n"

        prompt = f"""
    {context_str}

    ### ROLE
    You are a professional Database Architect. With strong expertise in designing and documenting database schemas using Mermaid syntax.
    
    ### CONTEXT
    Create a detailed Entity-Relationship Diagram (ERD) in Mermaid format for the following requirement: {user_message}

    Create a comprehensive database schema showing:
    1. All entities (tables) with their attributes (columns)
    2. Data types for each column (string, int, uuid, decimal, timestamp, etc.)
    3. Primary keys (PK), Foreign keys (FK), Unique constraints
    4. Relationships between entities (one-to-one, one-to-many, many-to-many)
    5. Cardinality notation (||--o{{ for one-to-many, etc.)

    ### INSTRUCTIONS
    1. Read and analyze the context in {context_str} and **<CONTEXT** section above.
    2. Create a comprehensive ERD diagram covering all specified elements.
    3. Ensure clarity, correctness, and proper Mermaid syntax.
    
    ### NOTE
    1. Use Mermaid erDiagram markdown format for the ERD diagram.
    2. Follow best practices for database design and normalization.
    3. Return ONLY the Mermaid code block.
    
    ### EXAMPLE OUTPUT
    Use Mermaid erDiagram syntax:
    ```mermaid
    erDiagram
        CUSTOMER ||--o{{ ORDER : places
        CUSTOMER {{
            uuid id PK
            string email
            string name
            string phone
            timestamp created_at
        }}
        ORDER ||--|{{ ORDER_ITEM : contains
        ORDER {{
            uuid id PK
            uuid customer_id FK
            decimal total
            string status
            timestamp created_at
        }}
        ORDER_ITEM {{
            uuid id PK
            uuid order_id FK
            uuid product_id FK
            int quantity
            decimal price
        }}
        PRODUCT ||--o{{ ORDER_ITEM : "ordered in"
        PRODUCT {{
            uuid id PK
            string name
            string description
            decimal price
            int stock
        }}
    ```

    IMPORTANT: 
    - Return ONLY the Mermaid code block starting with ```mermaid and ending with ```
    - Use proper cardinality notation: ||--o{{ (one-to-many), }}o--o{{ (many-to-many), ||--|| (one-to-one)
    - Include all entity attributes with data types
    - Mark primary keys with PK and foreign keys with FK
    - No additional text or explanations
    """

        completion = model_client.client.chat.completions.create(
            extra_headers=model_client.get_extra_headers(),
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Database Architect who creates detailed ERD diagrams in Mermaid syntax."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL
        )

        markdown_diagram = completion.choices[0].message.content

        # Create response with database-schema type and markdown detail
        schema_response = LLDDBResponse(
            type="database-schema",
            detail=markdown_diagram
        )
        output = LLDDBOutput(type="database-schema", response=schema_response)

        return {"response": output.model_dump()["response"]}

    except Exception as e:
        logger.error(f"Error generating database schema: {e}")
        # Fallback response
        return {
            "response": {
                "type": "database-schema",
                "detail": f"Error generating database schema: {str(e)}"
            }
        }

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
