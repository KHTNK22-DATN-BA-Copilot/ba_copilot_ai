# workflows/wireframe_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figma_mcp import generate_figma_wireframe
from models.wireframe import WireframeOutput, WireframeResponse, WireframeHTMLCSSOutput
from typing import Dict, TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from .html_css_generator import generate_html_css

class WireframeState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

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

def generate_wireframe_html_css(state: WireframeState) -> Dict:
    """Generate wireframe with HTML, CSS"""
    try:
        # Get context from state
        user_message = state.get("user_message", "")
        extracted_text = state.get("extracted_text", "")
        chat_context = state.get("chat_context", "")

        result = generate_html_css(user_message, extracted_text, chat_context)

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

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_wireframe_html_css", generate_wireframe_html_css)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_wireframe_html_css")
workflow.add_edge("generate_wireframe_html_css", END)

# Compile graph
wireframe_graph = workflow.compile()
