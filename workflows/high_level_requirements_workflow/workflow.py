# workflows/high_level_requirements_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL

class HighLevelRequirementsState(TypedDict):
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

def generate_high_level_requirements(state: HighLevelRequirementsState) -> HighLevelRequirementsState:
    """Generate High-Level Requirements document using OpenRouter AI"""
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

    You are a professional Business Analyst. Create a comprehensive High-Level Requirements document for the following project:

    Project Requirements: {user_message}

    Return the response in JSON format with this structure:
    {{
        "title": "High-Level Requirements - [Project Name]",
        "content": "Complete markdown document with sections:
            1. Introduction (Purpose, Scope, Business Objectives)
            2. Stakeholder Requirements (for each user type)
            3. Functional Requirements (organized by categories with FR-XXX identifiers)
            4. Non-Functional Requirements (Performance, Security, Usability, Reliability with NFR-XXX identifiers)
            5. Constraints (Budget, Timeline, Technical, Regulatory)
            6. Assumptions
            7. Dependencies
            8. Acceptance Criteria
            9. Next Steps
            10. Approval section with signature table"
    }}

    Include:
    - Clearly categorized functional requirements with unique identifiers (FR-UM-001, FR-PC-001, etc.)
    - Non-functional requirements with metrics (NFR-P-001: Page load < 2 seconds, etc.)
    - Tables for constraints, assumptions, and dependencies
    - Specific, measurable acceptance criteria

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
        doc_data = extract_json(result_content)

        response_data = {
            "title": doc_data.get("title", "High-Level Requirements Document"),
            "content": doc_data.get("content", "")
        }

        return {"response": response_data}

    except Exception as e:
        print(f"Error generating High-Level Requirements: {e}")
        # Fallback response
        return {
            "response": {
                "title": "High-Level Requirements Document",
                "content": f"Error generating document: {str(e)}"
            }
        }

# Build LangGraph pipeline for High-Level Requirements
workflow = StateGraph(HighLevelRequirementsState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_high_level_requirements", generate_high_level_requirements)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_high_level_requirements")
workflow.add_edge("generate_high_level_requirements", END)

# Compile graph
high_level_requirements_graph = workflow.compile()
