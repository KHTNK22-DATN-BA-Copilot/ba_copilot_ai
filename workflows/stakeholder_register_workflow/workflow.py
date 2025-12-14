# workflows/stakeholder_register_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

class StakeholderRegisterState(TypedDict):
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

def generate_stakeholder_register(state: StakeholderRegisterState) -> StakeholderRegisterState:
    """Generate Stakeholder Register document using OpenRouter AI"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    prompt = f"""
    You are a professional Business Analyst. Create a comprehensive Stakeholder Register document for the following project:

    Project Requirements: {state['user_message']}

    Return the response in JSON format with this structure:
    {{
        "title": "Stakeholder Register - [Project Name]",
        "content": "Complete markdown document with sections:
            1. Document Information (Date, Version, Prepared by)
            2. Executive Summary
            3. Stakeholder List (Internal and External with details)
            4. Stakeholder Analysis Matrix
            5. Communication Plan
            6. Engagement Activities
            7. Risk Assessment
            8. Conclusion"
    }}

    For each stakeholder include:
    - Name and Role
    - Department/Organization
    - Interest Level (High/Medium/Low)
    - Influence Level (High/Medium/Low)
    - Engagement Strategy
    - Communication Preferences
    - Key Concerns

    Include a stakeholder analysis matrix table showing Power, Interest, and Management Strategy.

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
            "title": doc_data.get("title", "Stakeholder Register"),
            "content": doc_data.get("content", "")
        }

        return {
            "user_message": state.get("user_message",""),
            "response": response_data
        }

    except Exception as e:
        print(f"Error generating Stakeholder Register: {e}")
        # Fallback response
        return {
            "user_message": "",
            "response": {
                "title": "Stakeholder Register",
                "content": f"Error generating document: {str(e)}"
            }
        }

# Build LangGraph pipeline for Stakeholder Register
workflow = StateGraph(StakeholderRegisterState)

# Add node
workflow.add_node("generate_stakeholder_register", generate_stakeholder_register)

# Set entry point and finish
workflow.set_entry_point("generate_stakeholder_register")
workflow.add_edge("generate_stakeholder_register", END)

# Compile graph
stakeholder_register_graph = workflow.compile()
