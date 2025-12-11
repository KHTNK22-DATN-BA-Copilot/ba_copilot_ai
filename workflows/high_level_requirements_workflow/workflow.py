# workflows/high_level_requirements_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

class HighLevelRequirementsState(TypedDict):
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

def generate_high_level_requirements(state: HighLevelRequirementsState) -> HighLevelRequirementsState:
    """Generate High-Level Requirements document using OpenRouter AI"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    prompt = f"""
    You are a professional Business Analyst. Create a comprehensive High-Level Requirements document for the following project:

    Project Requirements: {state['user_message']}

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

# Add node
workflow.add_node("generate_high_level_requirements", generate_high_level_requirements)

# Set entry point and finish
workflow.set_entry_point("generate_high_level_requirements")
workflow.add_edge("generate_high_level_requirements", END)

# Compile graph
high_level_requirements_graph = workflow.compile()
