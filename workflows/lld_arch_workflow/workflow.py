"""
LLD Architecture Workflow
Generates detailed low-level design architecture diagrams (component, deployment) using Mermaid.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List
import json
import logging
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, set_request_model_config, reset_request_model_config, MODEL
from models.lld_arch import LLDArchResponse, LLDArchOutput
from ..utils import extractor
from response import success_response, error_response

logger = logging.getLogger(__name__)

class LLDArchState(TypedDict):
    """State for LLD Architecture workflow"""
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List[str]]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_lld_arch_diagram(state: LLDArchState, config: Optional[dict] = None):
    """
    Generate detailed low-level architecture diagram using LLM.
    Creates component diagrams, deployment diagrams, or detailed system architecture.
    """
    model_client = get_model_client()
    cfg = (config or {}).get("configurable", {})
    token = set_request_model_config(
        provider=cfg.get("provider"),
        model_name=cfg.get("model_name"),
        api_key=cfg.get("api_key"),
    )
    try:
        
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
        Expert Software Architect (Low-Level Design, Mermaid).

        ### TASK
        Create a detailed LLD architecture diagram for: {user_message}

        ### REQUIREMENTS
        - Use Mermaid flowchart (graph TD or TB)
        - Include:
        - Components (services, modules, interfaces)
        - Internal structure and dependencies
        - Deployment elements (nodes, containers, network)
        - Data flow (directional)
        - Layers (presentation, application, data)
        - Use subgraphs for layers, subsystems, or deployment zones
        - Clearly label all nodes and connections
        - Choose appropriate style (component, deployment, or hybrid)
        - Ensure logical structure and readability

        ### OUTPUT (STRICT JSON ONLY)
        {{
        "content": "Mermaid diagram starting with 'graph TD' or 'graph TB' (with backticks, use \\n for newlines)",
        "summary": "One-line concise description of the architecture"
        }}

        ### RULES
        - ALWAYS include triple backticks (` ``` `) around the Mermaid diagram
        - ALWAYS start the Mermaid content with `graph TD` or `graph TB`
        - The `content` field MUST contain a complete Mermaid markdown block
        - Use escaped newlines (`\\n`) inside JSON strings
        - Return VALID parsable JSON only
        - Do NOT return markdown outside the JSON object
        - Do NOT add explanations, comments, or extra text
        - Do NOT add extra JSON keys
        - Ensure Mermaid syntax is valid and renderable, root must always have "content" and "summary" as specified - no nesting
        """

        response = model_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=cfg.get("model_name") or MODEL,
        )
        raw_output = response.choices[0].message.content or ""

        json_data = extractor.extract_json(raw_output)
        summary = "LLD Architecture"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "LLD Architecture")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": success_response(summary, content)
        } # pyright: ignore[reportReturnType]

    except Exception as e:
        logger.error(f"Error generating LLD architecture diagram: {e}")
        return {
            "response": error_response(
                "LLD Architecture",
                f"Error generating LLD architecture diagram: {e}",
            )
        } # pyright: ignore[reportReturnType]
    finally:
        reset_request_model_config(token)
        
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
