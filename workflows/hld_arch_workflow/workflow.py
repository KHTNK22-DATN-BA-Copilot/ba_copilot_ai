# workflows/hld_arch_workflow/workflow.py
from langgraph.graph import StateGraph, END

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.hld_arch import HLDArchOutput, HLDArchResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
import logging

logger = logging.getLogger(__name__)

class HLDArchState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]
    raw_diagram: Optional[str]
    validation_result: Optional[dict]
    retry_count: int

def generate_hld_arch_diagram(state: HLDArchState) -> HLDArchState:
    """Generate High-Level Design Architecture Diagram in Mermaid format"""
    model_client = get_model_client()

    # Build comprehensive prompt with context
    user_message = state['user_message']
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

    You are a professional Solution Architect. Create a High-Level Design (HLD) System Architecture Diagram in Mermaid markdown format based on the requirement: {user_message}

    The diagram should show:
    - **System Components**: Major system modules/services (Frontend, Backend, Database, etc.)
    - **External Systems**: Third-party integrations, APIs, external services
    - **Data Flow**: How data moves between components
    - **Technology Layers**: Presentation, Application, Data layers
    - **Infrastructure**: Load balancers, caching, message queues
    - **Security Boundaries**: Authentication, API Gateway, firewalls

    Use Mermaid graph syntax (flowchart) with:
    - Clear component names and labels
    - Directional arrows showing data flow
    - Subgraphs for logical grouping (e.g., Frontend Layer, Backend Layer)
    - Proper notation for different component types

    IMPORTANT: Return ONLY the Mermaid markdown code block for the architecture diagram, starting with ```mermaid and ending with ```.
    Do not include any explanatory text before or after the code block.

    Example format:
    ```mermaid
    graph TB
        subgraph "Client Layer"
            WebApp[Web Application]
            MobileApp[Mobile App]
        end
        
        subgraph "Application Layer"
            API[API Gateway]
            Auth[Authentication Service]
            BizLogic[Business Logic Service]
        end
        
        subgraph "Data Layer"
            DB[(Database)]
            Cache[(Redis Cache)]
        end
        
        WebApp --> API
        MobileApp --> API
        API --> Auth
        API --> BizLogic
        BizLogic --> DB
        BizLogic --> Cache
    ```
    """

    try:
        completion = model_client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL
        )

        markdown_diagram = completion.choices[0].message.content

        # Create response with diagram type and markdown detail
        diagram_response = HLDArchResponse(
            type="hld-arch",
            detail=markdown_diagram
        )
        output = HLDArchOutput(type="diagram", response=diagram_response)

        return {"response": output.model_dump()["response"]}

    except Exception as e:
        logger.error(f"Error generating HLD architecture diagram: {e}")
        # Fallback response
        return {
            "response": {
                "type": "hld-arch",
                "detail": f"Error generating architecture diagram: {str(e)}"
            }
        }

# Build LangGraph pipeline for HLD Architecture
workflow = StateGraph(HLDArchState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_hld_arch", generate_hld_arch_diagram)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_hld_arch")
workflow.add_edge("generate_hld_arch", END)

# Compile graph
hld_arch_graph = workflow.compile()
