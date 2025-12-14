# workflows/srs_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.srs import SRSOutput, SRSResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL

class SRSState(TypedDict):
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

def generate_srs(state: SRSState) -> SRSState:
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

    You are a professional Business Analyst. Create a detailed Software Requirements Specification (SRS)
    document for the following requirement: {user_message}

    Return the response in JSON format:
    {{
        "title": "Project/feature name",
        "functional_requirements": "Description of functional requirements (main features, use cases)",
        "non_functional_requirements": "Description of non-functional requirements (performance, security, scalability, etc.)",
        "detail": "Complete detailed SRS document content in Markdown format with sections:
                   1. Introduction
                   2. Overall Description
                   3. Functional Requirements (detailed)
                   4. Non-Functional Requirements (detailed)
                   5. System Features
                   6. External Interface Requirements
                   7. Other Requirements"
    }}

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
        srs_data = extract_json(result_content)

        srs_response = SRSResponse(
            title=srs_data.get("title", "Software Requirements Specification"),
            functional_requirements=srs_data.get("functional_requirements", ""),
            non_functional_requirements=srs_data.get("non_functional_requirements", ""),
            detail=srs_data.get("detail", "")
        )

        output = SRSOutput(type="srs", response=srs_response)
        return {"response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error generating SRS: {e}")
        # Fallback response
        return {
            "response": {
                "title": "Software Requirements Specification",
                "functional_requirements": "Error generating requirements",
                "non_functional_requirements": "Error generating requirements",
                "detail": f"Error: {str(e)}"
            }
        }

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
