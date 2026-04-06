"""
LLD API Specifications Workflow
Generates detailed API endpoint specifications in OpenAPI/Swagger format.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List
import json
import logging
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
# from models.lld_api import LLDAPIResponse, LLDAPIOutput
import re
from ..utils import extractor

logger = logging.getLogger(__name__)

class LLDAPIState(TypedDict):
    """State for LLD API Specifications workflow"""
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List[str]]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def extract_json(text: str) -> dict:
    try:
        # Step 1: extract JSON block
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            return {}
        json_str = match.group(0)
        # Step 2: first parse
        data = json.loads(json_str)
        # Step 3: handle double-encoded JSON (VERY IMPORTANT)
        if isinstance(data, str):
            data = json.loads(data)
        return data
    except Exception as e:
        print(f"[extract_json ERROR] {e}")
        print(f"[extract_json RAW]\n{text}")
        return {}

def generate_lld_api_specs(state: LLDAPIState):
    """
    Generate detailed API specifications document using LLM.
    Creates comprehensive API documentation with endpoints, models, authentication.
    """
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
    API Architect (REST, OpenAPI-style).

    ### TASK
    Design a Low-Level API Specification for: {user_message}

    ### REQUIREMENTS
    The "content" MUST be a Markdown document (use \\n) with EXACT structure:

    # API Specification - <Project Name>

    ## 1. API Overview
    - Purpose, base URL, format (JSON), REST style

    ## 2. Authentication
    - Method (JWT/API key), token flow, security notes

    ## 3. Endpoints
    - Group by resource
    - For each endpoint include:
    - Method + path + description
    - Parameters (path/query/body)
    - Request/response JSON examples
    - Status codes

    ## 4. Data Models
    - Fields: name, type, required, validation, example

    ## 5. Error Handling
    - Standard HTTP codes + response format

    ## 6. Rate Limiting
    - Limits, headers, throttling

    ## 7. Versioning
    - Strategy + deprecation

    ## 8. Examples
    - cURL, JavaScript, Python

    - Use concise formatting and clear examples
    - Do NOT leave any section empty

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Markdown document following REQUIRED structure (use \\n for newlines)",
    "summary": "One-line API summary"
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
        summary = "LLD API"
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "LLD API")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating Low-level-design API Specs: {e}")
        # Fallback response

# Build LangGraph pipeline for LLD API Specifications
workflow = StateGraph(LLDAPIState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_lld_api", generate_lld_api_specs)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_lld_api")
workflow.add_edge("generate_lld_api", END)

# Compile graph
lld_api_graph = workflow.compile()
