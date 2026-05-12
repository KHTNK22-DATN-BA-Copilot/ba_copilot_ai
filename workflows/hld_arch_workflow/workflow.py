# workflows/hld_arch_workflow/workflow.py
from langgraph.graph import StateGraph, END

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from models.hld_arch import HLDArchOutput, HLDArchResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
import logging
from ..utils import extractor
from response import success_response, error_response

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

def generate_hld_arch_diagram(state: HLDArchState):
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

    ### ROLE
    Solution Architect (HLD, Mermaid).

    ### TASK
    Create a High-Level System Architecture Diagram for: {user_message}

    ### REQUIREMENTS
    Include:
    - System components (frontend, backend, database, services)
    - External systems (APIs, third-party)
    - Data flow (directional)
    - Layers (presentation, application, data)
    - Infrastructure (LB, cache, queues)
    - Security boundaries (auth, gateway, firewall)

    Use:
    - Mermaid flowchart (`graph TD` or `graph TB`)
    - Subgraphs for architectural layers
    - Clear labels and directional connections
    - Consistent node naming
    - Logical grouping of related services
    - Readable and valid Mermaid structure

    ### OUTPUT (STRICT JSON ONLY)
    {{
      "content": "```mermaid\\ngraph TD\\n...\\n```",
      "summary": "One-line description of the architecture"
    }}

    ### RULES
    - ALWAYS include triple backticks (` ``` `) around the Mermaid diagram
    - ALWAYS start the Mermaid content with `graph TD` or `graph TB`
    - The `content` field MUST contain a complete Mermaid markdown block
    - Use escaped newlines (`\\n`) inside JSON strings
    - Return VALID parsable JSON only
    - Do NOT return markdown outside the JSON object
    - Do NOT add explanations, comments, or extra text
    - Ensure Mermaid syntax is valid and renderable, root must always have "content" and "summary" as specified - no nesting
    """

    try:
        raw_output = model_client.gemini_completion(prompt)

        json_data = extractor.extract_json(raw_output)
        summary = "HLD architecture diagram"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "HLD architecture diagram")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": success_response(summary, content)
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        logger.error(f"Error generating HLD architecture diagram: {e}")
        return {
            "response": error_response(
                "HLD architecture diagram",
                f"Error generating HLD architecture diagram: {e}",
            )
        } # pyright: ignore[reportReturnType]

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
