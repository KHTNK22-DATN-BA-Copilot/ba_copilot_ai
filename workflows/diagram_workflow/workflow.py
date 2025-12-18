# workflows/diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figma_mcp import generate_figma_diagram
from models.diagram import DiagramOutput, DiagramResponse
from typing import TypedDict
from connect_model import get_model_client, MODEL

class DiagramState(TypedDict):
    user_message: str
    response: dict

def generate_diagram_description(state: DiagramState) -> DiagramState:
    """Generate diagram description using OpenRouter AI"""
    model_client = get_model_client()

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
        completion = model_client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL
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