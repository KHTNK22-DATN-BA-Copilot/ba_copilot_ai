# workflows/requirements_management_plan_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL

class RequirementsManagementPlanState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
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

def generate_requirements_management_plan(state: RequirementsManagementPlanState) -> RequirementsManagementPlanState:
    """Generate Requirements Management Plan document using OpenRouter AI"""
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
    You are a Business Analyst.

    TASK:
    Generate a Requirements Management Plan.

    PROJECT:
    {user_message}

    CONTEXT:
    {context_str}

    OUTPUT RULES (STRICT):
    - Return ONLY valid JSON
    - No explanation, no markdown outside JSON
    - Escape all newlines as \\n inside JSON

    FORMAT:
    {{
    "title": "Requirements Management Plan - <Project Name>",
    "content": "<FULL markdown document here>"
    }}

    CONTENT REQUIREMENTS:
    - Use markdown inside "content"
    - Include all sections:
    1. Introduction
    2. Requirements Management Approach
    3. Elicitation
    4. Analysis (MoSCoW)
    5. Documentation
    6. Validation
    7. Traceability (with table)
    8. Change Management
    9. Communication Plan (table)
    10. Roles & Responsibilities
    11. Tools
    12. Metrics
    13. QA
    14. Training
    15. Appendices
    16. Approval

    - MUST NOT return empty content
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

# Build LangGraph pipeline for Requirements Management Plan
workflow = StateGraph(RequirementsManagementPlanState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_requirements_management_plan", generate_requirements_management_plan)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_requirements_management_plan")
workflow.add_edge("generate_requirements_management_plan", END)

# Compile graph
requirements_management_plan_graph = workflow.compile()
