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
from models.lld_api import LLDAPIResponse, LLDAPIOutput
import re

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

def generate_lld_api_specs(state: LLDAPIState) -> LLDAPIState:
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
    You are an API Architect.

    TASK:
    Generate a Low-Level API Specification (REST, OpenAPI-style).

    PROJECT:
    {user_message}

    CONTEXT:
    {context_str}

    OUTPUT RULES (STRICT):
    - Return ONLY valid JSON
    - No explanation, no markdown outside JSON
    - ALL values MUST be strings (no arrays/objects)
    - Escape newlines as \\n

    FORMAT:
    {{
    "title": "API Specifications - <Project Name>",
    "content": "<FULL markdown document here>"
    }}

    CONTENT REQUIREMENTS:

    api_overview:
    - purpose, base URL, formats (JSON), architecture (REST)

    authentication:
    - method (JWT/API key), token flow, security notes

    endpoints:
    - MUST be a STRING
    - include: method, path, description
    - include: parameters (path/query/body)
    - include: request/response JSON examples
    - include: status codes
    - format clearly (markdown-like inside string)

    data_models:
    - MUST be a STRING
    - include: field name, type, required, validation, example

    error_handling:
    - standard HTTP codes + format

    rate_limiting:
    - requests/minute, headers, throttling

    versioning:
    - strategy + deprecation

    detail:
    - FULL markdown document including:
    - overview
    - authentication
    - endpoints grouped by resource
    - data models
    - examples (cURL, JS, Python)

    IMPORTANT:
    - DO NOT return empty fields
    - DO NOT include any text outside JSON
    """
    try:
        # Using OpenRouter (default)
        completion = model_client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL
        )
        result_content = completion.choices[0].message.content

        # Using Gemini 2.5 Flash Lite
        # result_content = model_client.gemini_completion(prompt)

        doc_data = extract_json(str(result_content))
        # Handle nested/double JSON
        if isinstance(doc_data.get("content"), str):
            try:
                inner = extract_json(doc_data["content"])
                if inner:
                    doc_data = inner
            except:
                pass
        response_data = {
            "title": doc_data.get("title", "Requirements Management Plan"),
            "content": doc_data.get("content", "")
        }
        # Fallback if still broken
        if not doc_data or not doc_data.get("content"):
            print("⚠️ Falling back to raw output")
            response_data = {
                "title": "Requirements Management Plan",
                "content": result_content
            }
        return {"response": response_data} # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating Requirements Management Plan: {e}")
        # Fallback response
        return {
            "response": {
                "type": "Requirements Management Plan",
                "content": f"Error generating document: {str(e)}"
            }
        } # pyright: ignore[reportReturnType]

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
