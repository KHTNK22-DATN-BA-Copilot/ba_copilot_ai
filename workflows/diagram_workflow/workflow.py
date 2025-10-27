# workflows/diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figma_mcp import generate_figma_diagram
from models.diagram import DiagramOutput, DiagramResponse
from typing import TypedDict

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

class DiagramState(TypedDict):
    user_message: str
    response: dict

def generate_diagram_description(state: DiagramState) -> DiagramState:
    """Generate diagram description using OpenRouter AI"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    prompt = f"""
    Create a detailed description for a diagram based on the requirement: {state['user_message']}

    The description should include:
    - Type of diagram (ERD, Flowchart, Architecture, etc.)
    - Main entities/components
    - Relationships/connections between components
    - Important attributes/properties

    Return a detailed description that can be used to draw the diagram.
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

        description = completion.choices[0].message.content

        # Generate Figma diagram using the description
        result = generate_figma_diagram(description)

        diagram_response = DiagramResponse(**result)
        output = DiagramOutput(type="diagram", response=diagram_response)

        return {"response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error generating diagram: {e}")
        # Fallback response
        return {
            "response": {
                "figma_link": "",
                "editable": False,
                "description": f"Error generating diagram: {str(e)}"
            }
        }

# Build LangGraph pipeline for Diagram
workflow = StateGraph(DiagramState)

# Add node
workflow.add_node("generate_diagram", generate_diagram_description)

# Set entry point and finish
workflow.set_entry_point("generate_diagram")
workflow.add_edge("generate_diagram", END)

# Compile graph
diagram_graph = workflow.compile()
