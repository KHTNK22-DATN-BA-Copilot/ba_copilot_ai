"""
LLD Architecture Workflow
Generates detailed low-level design architecture diagrams (component, deployment) using Mermaid.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List
import json
import logging
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from models.lld_arch import LLDArchResponse, LLDArchOutput

logger = logging.getLogger(__name__)

class LLDArchState(TypedDict):
    """State for LLD Architecture workflow"""
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List[str]]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_lld_arch_diagram(state: LLDArchState) -> LLDArchState:
    """
    Generate detailed low-level architecture diagram using LLM.
    Creates component diagrams, deployment diagrams, or detailed system architecture.
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

    You are a professional Software Architect. Create a detailed LOW-LEVEL DESIGN architecture diagram
    in Mermaid format for the following requirement: {user_message}

    Create a comprehensive component or deployment diagram showing:
    1. Component Diagrams - Detailed components, interfaces, dependencies, internal structure
    2. Deployment Diagrams - Hardware nodes, software components, network topology, deployment artifacts
    3. Detailed System Architecture - All layers, components, data flows, integration points

    Return ONLY the Mermaid diagram code block. No explanations before or after.
    
    Use appropriate Mermaid syntax:
    - For component diagrams: Use graph/flowchart with detailed component boxes
    - For deployment diagrams: Use graph with nodes representing servers/containers
    - Include subgraphs for logical groupings (layers, subsystems, deployment zones)
    - Show all connections, dependencies, and data flows
    - Add descriptive labels and annotations
    
    Example structure:
    ```mermaid
    graph TB
        subgraph "Presentation Layer"
            UI[Web UI Component]
            API[API Gateway]
        end
        
        subgraph "Application Layer"
            Auth[Authentication Service]
            Business[Business Logic Engine]
            Cache[Cache Manager]
        end
        
        subgraph "Data Layer"
            DB[(Primary Database)]
            Queue[Message Queue]
        end
        
        UI --> API
        API --> Auth
        API --> Business
        Business --> Cache
        Business --> DB
        Business --> Queue
    ```

    IMPORTANT: Return ONLY the Mermaid code block starting with ```mermaid and ending with ```
    No additional text or explanations.
    """

        completion = model_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Software Architect who creates detailed low-level design diagrams in Mermaid syntax."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL
        )

        markdown_diagram = completion.choices[0].message.content

        # Create response with diagram type and markdown detail
        diagram_response = LLDArchResponse(
            type="lld-arch",
            detail=markdown_diagram
        )
        output = LLDArchOutput(type="diagram", response=diagram_response)

        return {"response": output.model_dump()["response"]}

    except Exception as e:
        logger.error(f"Error generating LLD architecture diagram: {e}")
        # Fallback response
        return {
            "response": {
                "type": "lld-arch",
                "detail": f"Error generating architecture diagram: {str(e)}"
            }
        }

# Build LangGraph pipeline for LLD Architecture
workflow = StateGraph(LLDArchState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_lld_arch", generate_lld_arch_diagram)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_lld_arch")
workflow.add_edge("generate_lld_arch", END)

# Compile graph
lld_arch_graph = workflow.compile()
