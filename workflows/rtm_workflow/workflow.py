# workflows/rtm_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from ..utils import extractor

class RTMState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def extract_json(text: str) -> dict:
    """Extract JSON from text response"""
    try:
        # Find JSON block
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        return {}
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return {}


def generate_rtm(state: RTMState):
    """Generate Requirements Traceability Matrix document using OpenRouter AI"""
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
    Business Analyst / QA Specialist (traceability, quality).

    ### TASK
    Create a Requirements Traceability Matrix (RTM) for: {user_message}

    ### REQUIREMENTS
    The "content" MUST be a Markdown document (use \\n) with EXACT structure:

    # Requirements Traceability Matrix - <Project Name>

    ## 1. Document Information
    - Date, version, author

    ## 2. Executive Summary
    - Overview of traceability and coverage

    ## 3. Purpose and Scope

    ## 4. Traceability Matrix Overview

    ## 5. Requirements Traceability Matrix
    - Include table with columns:
    ID | Description | Priority | Source | Design | Implementation | Test Cases | Test Status | Coverage | Verification

    ## 6. Forward Traceability
    - Requirements → Design → Implementation → Test Cases

    ## 7. Backward Traceability
    - Test Cases → Implementation → Design → Requirements

    ## 8. Coverage Analysis
    - Coverage % and key insights

    ## 9. Gap Analysis
    - Missing links, untested requirements

    ## 10. Change Impact Assessment

    ## 11. Quality Metrics
    - Coverage, pass rate, defect trends

    ## 12. Conclusion and Recommendations

    - Use concise bullet points (except table)
    - Do NOT leave any section empty

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Markdown document following REQUIRED structure (use \\n for newlines)",
    "summary": "One-line RTM summary"
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
        summary = "RTM"
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "RTM")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating RTM: {e}")

# Build LangGraph pipeline for RTM
workflow = StateGraph(RTMState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_rtm", generate_rtm)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_rtm")
workflow.add_edge("generate_rtm", END)

# Compile graph
rtm_graph = workflow.compile()
