# workflows/srs_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.srs import SRSOutput, SRSResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from ..utils import extractor

class SRSState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_srs(state: SRSState):
    """Generate SRS document using OpenRouter AI"""
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
    Business Analyst (SRS, IEEE-style).

    ### TASK
    Create a Software Requirements Specification (SRS) for: {user_message}

    ### REQUIREMENTS
    The "content" MUST be a Markdown document (use \\n) with EXACT structure:

    # Software Requirements Specification - <Project Name>

    ## 1. Introduction
    - Purpose, scope, definitions

    ## 2. Overall Description
    - Product perspective, users, assumptions

    ## 3. Functional Requirements
    - Features, use cases, system behaviors

    ## 4. Non-Functional Requirements
    - Performance, security, scalability, usability, compliance

    ## 5. System Features
    - Detailed feature breakdown

    ## 6. External Interface Requirements
    - UI, APIs, hardware, integrations

    ## 7. Other Requirements
    - Constraints, legal, standards

    - Use concise bullet points
    - Do NOT leave any section empty

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Markdown document following REQUIRED structure (use \\n for newlines)",
    "summary": "One-line SRS summary"
    }}

    ### RULES
    - Output JSON ONLY (no markdown wrappers, no explanations)
    - No extra keys, no missing keys
    - Do NOT change section titles or order
    - Escape \\n properly
    - All values must be strings
    """

    try:
        raw_output = model_client.gemini_completion(prompt)

        json_data = extractor.extract_json(raw_output)
        summary = "SRS"
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "SRS")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating SRS: {e}")

# Build LangGraph pipeline for SRS
workflow = StateGraph(SRSState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_srs", generate_srs)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_srs")
workflow.add_edge("generate_srs", END)

# Compile graph
srs_graph = workflow.compile()
