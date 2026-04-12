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
    - Mermaid flowchart (graph TD/TB)
    - Subgraphs for layers
    - Clear labels and connections

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Mermaid diagram starting with 'graph TD' or 'graph TB' (with backticks, use \\n for newlines)",
    "summary": "One-line description of the architecture"
    }}

    ### RULES
    - Do include ``` as markdown wrappers
    - Valid Mermaid syntax only
    - No extra keys, no extra text
    - Ensure JSON is parsable (escape \\n properly)
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
        summary = "HLD architecture diagram"
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "HLD architecture diagram")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        logger.error(f"Error generating HLD architecture diagram: {e}")

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
