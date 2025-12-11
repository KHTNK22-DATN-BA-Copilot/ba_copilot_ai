# workflows/requirements_management_plan_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

class RequirementsManagementPlanState(TypedDict):
    user_message: str
    response: dict

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

def generate_requirements_management_plan(state: RequirementsManagementPlanState) -> RequirementsManagementPlanState:
    """Generate Requirements Management Plan document using OpenRouter AI"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    prompt = f"""
    You are a professional Business Analyst. Create a comprehensive Requirements Management Plan for the following project:

    Project Requirements: {state['user_message']}

    Return the response in JSON format with this structure:
    {{
        "title": "Requirements Management Plan - [Project Name]",
        "content": "Complete markdown document with sections:
            1. Introduction (Purpose, Scope, Objectives)
            2. Requirements Management Approach (Methodology Alignment, Requirements Levels)
            3. Requirements Elicitation (Techniques, Schedule with table)
            4. Requirements Analysis (Techniques, Prioritization using MoSCoW)
            5. Requirements Documentation (Standards, Tools, Attributes)
            6. Requirements Validation (Techniques, Acceptance Criteria Checklist)
            7. Requirements Traceability (Matrix, Tools)
            8. Requirements Change Management (Process, Change Control Board, Criteria)
            9. Communication Plan (Table with Audience, Method, Frequency, Content)
            10. Roles and Responsibilities (Product Owner, BA, Scrum Master, Dev Team, Stakeholders)
            11. Tools and Techniques
            12. Metrics and Reporting
            13. Quality Assurance
            14. Training and Support
            15. Appendices
            16. Document Approval section with signature table"
    }}

    Include:
    - User Story Format template
    - MoSCoW prioritization method
    - Change request process flowchart (in text format)
    - Requirements attributes list
    - Traceability matrix example table
    - Communication plan table
    - Metrics for tracking requirements (velocity, volatility, defect density)
    - Quality criteria checklist

    Return only JSON, no additional text.
    """

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "BA-Copilot",
            },
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result_content = completion.choices[0].message.content
        doc_data = extract_json(str(result_content))

        response_data = {
            "title": doc_data.get("title", "Requirements Management Plan"),
            "content": doc_data.get("content", "")
        }

        return {
            "user_message": state.get("user_message",""),
            "response": response_data
            }

    except Exception as e:
        print(f"Error generating Requirements Management Plan: {e}")
        # Fallback response
        return {
            "user_message": state.get("user_message",""),
            "response": {
                "title": "Requirements Management Plan",
                "content": f"Error generating document: {str(e)}"
            }
        }

# Build LangGraph pipeline for Requirements Management Plan
workflow = StateGraph(RequirementsManagementPlanState)

# Add node
workflow.add_node("generate_requirements_management_plan", generate_requirements_management_plan)

# Set entry point and finish
workflow.set_entry_point("generate_requirements_management_plan")
workflow.add_edge("generate_requirements_management_plan", END)

# Compile graph
requirements_management_plan_graph = workflow.compile()
