# workflows/wireframe_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figma_mcp import generate_figma_wireframe
from models.wireframe import WireframeOutput, WireframeResponse
from typing import TypedDict

class WireframeState(TypedDict):
    user_message: str
    response: dict

def generate_wireframe(state: WireframeState) -> WireframeState:
    """Generate wireframe using Figma MCP"""
    try:
        result = generate_figma_wireframe(state["user_message"])

        wireframe_response = WireframeResponse(**result)
        output = WireframeOutput(type="wireframe", response=wireframe_response)

        return {"response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error generating wireframe: {e}")
        # Fallback response
        return {
            "response": {
                "figma_link": "",
                "editable": False,
                "description": f"Error generating wireframe: {str(e)}"
            }
        }

# Build LangGraph pipeline for Wireframe
workflow = StateGraph(WireframeState)

# Add node
workflow.add_node("generate_wireframe", generate_wireframe)

# Set entry point and finish
workflow.set_entry_point("generate_wireframe")
workflow.add_edge("generate_wireframe", END)

# Compile graph
wireframe_graph = workflow.compile()
