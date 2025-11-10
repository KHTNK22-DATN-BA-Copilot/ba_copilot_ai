# workflows/wireframe_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figma_mcp import generate_figma_wireframe
from models.wireframe import WireframeOutput, WireframeResponse, WireframeHTMLCSSOutput
from typing import Dict, TypedDict
from .html_css_generator import generate_html_css

class WireframeState(TypedDict):
    user_message: str
    response: dict

def generate_wireframe(state: WireframeState) -> WireframeState:
    """Generate wireframe using Figma MCP"""
    try:
        result = generate_figma_wireframe(state["user_message"])

        wireframe_response = WireframeResponse(**result)
        output = WireframeOutput(type="wireframe", response=wireframe_response)

        return {"response": output.model_dump()["response"]} # pyright: ignore[reportReturnType]

    except Exception as e:
        print(f"Error generating wireframe: {e}")
        # Fallback response
        return {
            "response": {
                "figma_link": "",
                "editable": False,
                "description": f"Error generating wireframe: {str(e)}"
            }
        } # pyright: ignore[reportReturnType]

def generate_wireframe_html_css(state: WireframeState) -> Dict:
    """Generate wireframe with HTML, CSS"""
    try:
        result = generate_html_css(state["user_message"])

        wireframe_response = WireframeHTMLCSSOutput(response=result)
        
        return {"response": wireframe_response.model_dump()["response"]}

    except Exception as e:
        print(f"Error creating HTML, CSS wireframe : {e}")
        import traceback
        traceback.print_exc()
        # Fallback response
        return {
            "response": {
                "content": f"Error creating HTML, CSS wireframe: {str(e)}"
            }
        }


# BUILDING THE WORKFLOW

workflow = StateGraph(WireframeState)

# Add node
# workflow.add_node("generate_wireframe", generate_wireframe)
workflow.add_node("generate_wireframe_html_css", generate_wireframe_html_css)

# Set entry point and finish
# workflow.set_entry_point("generate_wireframe")
# workflow.add_edge("generate_wireframe", END)

workflow.set_entry_point("generate_wireframe_html_css")
workflow.add_edge("generate_wireframe_html_css", END)

# Compile graph
wireframe_graph = workflow.compile()
