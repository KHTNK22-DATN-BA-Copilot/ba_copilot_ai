# workflows/feasibility_study_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.feasibility_study import FeasibilityStudyOutput, FeasibilityStudyResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL

class FeasibilityStudyState(TypedDict):
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

def generate_feasibility_study(state: FeasibilityStudyState) -> FeasibilityStudyState:
    """Generate Feasibility Study document using OpenRouter AI"""
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

    You are a professional Business Analyst. Create a comprehensive Feasibility Study Report
    for the following requirement: {user_message}

    Analyze the project from multiple feasibility dimensions:
    1. Technical Feasibility - Can the project be technically implemented with current technology?
    2. Operational Feasibility - Will the organization be able to operate and maintain the solution?
    3. Economic Feasibility - Is the project financially viable?
    4. Schedule Feasibility - Can the project be completed within the required timeframe?
    5. Legal Feasibility - Are there any legal or regulatory barriers?

    Return the response in JSON format:
    {{
        "title": "Feasibility Study - [Project Name]",
        "executive_summary": "Brief overview of feasibility analysis findings",
        "technical_feasibility": "Assessment of technical capability, infrastructure, and technology requirements",
        "operational_feasibility": "Analysis of organizational readiness, resources, and operational impact",
        "economic_feasibility": "Financial viability analysis including costs, benefits, and ROI projections",
        "schedule_feasibility": "Timeline analysis and assessment of project duration",
        "legal_feasibility": "Legal and regulatory compliance assessment",
        "detail": "Complete detailed feasibility study report in Markdown format with sections:
                   1. Executive Summary
                   2. Project Overview
                   3. Technical Feasibility Analysis
                   4. Operational Feasibility Analysis
                   5. Economic Feasibility Analysis
                   6. Schedule Feasibility Analysis
                   7. Legal Feasibility Analysis
                   8. Recommendations and Conclusion"
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
        feasibility_data = extract_json(result_content)

        feasibility_response = FeasibilityStudyResponse(
            title=feasibility_data.get("title", "Feasibility Study Report"),
            executive_summary=feasibility_data.get("executive_summary", ""),
            technical_feasibility=feasibility_data.get("technical_feasibility", ""),
            operational_feasibility=feasibility_data.get("operational_feasibility", ""),
            economic_feasibility=feasibility_data.get("economic_feasibility", ""),
            schedule_feasibility=feasibility_data.get("schedule_feasibility", ""),
            legal_feasibility=feasibility_data.get("legal_feasibility", ""),
            detail=feasibility_data.get("detail", "")
        )

        output = FeasibilityStudyOutput(type="feasibility-study", response=feasibility_response)
        return {"response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error generating feasibility study: {e}")
        # Fallback response
        return {
            "response": {
                "title": "Feasibility Study Report",
                "executive_summary": "Error generating feasibility study",
                "technical_feasibility": "Error",
                "operational_feasibility": "Error",
                "economic_feasibility": "Error",
                "schedule_feasibility": "Error",
                "legal_feasibility": "Error",
                "detail": f"Error: {str(e)}"
            }
        }

# Build LangGraph pipeline for Feasibility Study
workflow = StateGraph(FeasibilityStudyState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_feasibility_study", generate_feasibility_study)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_feasibility_study")
workflow.add_edge("generate_feasibility_study", END)

# Compile graph
feasibility_study_graph = workflow.compile()
