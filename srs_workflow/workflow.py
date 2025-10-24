# srs_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
from models.srs import SRSOutput, SRSResponse
import json
import os
from typing import TypedDict

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

class SRSState(TypedDict):
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

def generate_srs(state: SRSState) -> SRSState:
    """Generate SRS document using OpenRouter AI"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    prompt = f"""
    You are a professional Business Analyst. Create a detailed Software Requirements Specification (SRS)
    document for the following requirement: {state['user_message']}

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

# Add node
workflow.add_node("generate_srs", generate_srs)

# Set entry point and finish
workflow.set_entry_point("generate_srs")
workflow.add_edge("generate_srs", END)

# Compile graph
srs_graph = workflow.compile()
