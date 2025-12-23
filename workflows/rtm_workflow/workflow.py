# workflows/rtm_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL


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


def generate_rtm(state: RTMState) -> RTMState:
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

    You are a professional Business Analyst and Quality Assurance specialist. Create a comprehensive Requirements Traceability Matrix (RTM) document for the following project:

    Project Requirements: {user_message}

    Return the response in JSON format with this structure:
    {{
        "title": "Requirements Traceability Matrix - [Project Name]",
        "content": "Complete markdown document with the following sections:
            1. Document Information (Date, Version, Prepared by)
            2. Executive Summary
            3. Purpose and Scope
            4. Traceability Matrix Overview
            5. Requirements Traceability Matrix Table
            6. Forward Traceability (Requirements → Design → Implementation → Test Cases)
            7. Backward Traceability (Test Cases → Implementation → Design → Requirements)
            8. Coverage Analysis
            9. Gap Analysis
            10. Change Impact Assessment
            11. Quality Metrics
            12. Conclusion and Recommendations"
    }}

    The Traceability Matrix should include:
    - Requirement ID
    - Requirement Description
    - Priority (High/Medium/Low)
    - Source (Stakeholder/Document)
    - Design Reference
    - Implementation Module
    - Test Case ID(s)
    - Test Status (Passed/Failed/Pending/Not Started)
    - Coverage Status (Full/Partial/None)
    - Verification Method (Review/Inspection/Test/Demo)

    Include:
    - A comprehensive matrix table showing all requirements
    - Forward and backward traceability links
    - Coverage analysis with percentage metrics
    - Gap identification for missing test coverage
    - Risk assessment for untested requirements
    - Recommendations for improving coverage

    Return only JSON, no additional text.
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

        result_content = completion.choices[0].message.content
        doc_data = extract_json(str(result_content))

        response_data = {
            "title": doc_data.get("title", "Requirements Traceability Matrix"),
            "content": doc_data.get("content", "")
        }

        return {"response": response_data}

    except Exception as e:
        print(f"Error generating RTM: {e}")
        # Fallback response
        return {
            "response": {
                "title": "Requirements Traceability Matrix",
                "content": f"Error generating document: {str(e)}"
            }
        }


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
