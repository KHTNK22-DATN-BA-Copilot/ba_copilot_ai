"""
UI/UX Wireframe Workflow for Phase 6 - UI/UX Design Phase
Generates UI wireframes with layout and component specifications
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict
import json
import logging
from connect_model import get_model_client, MODEL

logger = logging.getLogger(__name__)


class UIUXWireframeState(TypedDict):
    """State for wireframe generation workflow"""
    message: str
    content_id: Optional[str]
    storage_paths: Optional[List[str]]
    response: Optional[Dict]
    extracted_text: Optional[str]
    chat_context: Optional[str]


def get_content_file(state: UIUXWireframeState) -> UIUXWireframeState:
    """Extract content from uploaded files"""
    storage_paths = state.get('storage_paths')
    
    if not storage_paths:
        print("No storage_paths provided, skipping file content retrieval")
        return {"extracted_text": ""}
    
    # TODO: Implement file extraction from Supabase Storage
    # For now, return empty string
    return {"extracted_text": ""}


def get_chat_history(state: UIUXWireframeState) -> UIUXWireframeState:
    """Retrieve chat history from content_id"""
    content_id = state.get('content_id')
    
    if not content_id:
        print("No content_id provided, skipping chat history")
        return {"chat_context": ""}
    
    # TODO: Implement chat history retrieval from database
    # For now, return empty string
    return {"chat_context": ""}


def generate_uiux_wireframe(state: UIUXWireframeState) -> UIUXWireframeState:
    """
    Generate UI/UX wireframe with layout and component specifications
    """
    try:
        model_client = get_model_client()
        
        user_message = state.get('message', '')
        extracted_text = state.get('extracted_text', '')
        chat_context = state.get('chat_context', '')
        
        # Build context
        context_parts = []
        if chat_context:
            context_parts.append(f"Context from previous conversation:\n{chat_context}\n")
        if extracted_text:
            context_parts.append(f"Extracted content from uploaded files:\n{extracted_text}\n")
        
        context_str = "\n".join(context_parts)
        
        prompt = f"""{context_str}

You are an expert UX/UI Designer specializing in wireframe design. Create a comprehensive UI/UX wireframe specification for:

{user_message}

Generate a detailed wireframe that includes:
1. Title and wireframe type (low-fidelity, high-fidelity, or interactive)
2. List of screens/pages to be designed
3. Layout structure (grid system, columns, spacing)
4. UI components (headers, navigation, forms, buttons, cards, etc.)
5. Navigation flow between screens
6. Design annotations and notes
7. Responsive behavior considerations (mobile, tablet, desktop)
8. Complete wireframe specification

Return ONLY a valid JSON object with this exact structure:
{{
  "title": "Wireframe title",
  "wireframe_type": "low-fidelity or high-fidelity or interactive",
  "screens": "List of screens: Screen 1, Screen 2, etc.",
  "layout_structure": "12-column grid, 8px spacing, max-width 1200px, etc.",
  "components": "Header with logo and navigation, Hero section, Card grid, Footer, etc.",
  "navigation_flow": "Home -> Product List -> Product Detail -> Cart -> Checkout",
  "annotations": "Key design decisions and rationale",
  "responsive_behavior": "Mobile: single column, Tablet: 2 columns, Desktop: 3 columns",
  "detail": "Complete wireframe specification with all details"
}}

IMPORTANT: Return ONLY the JSON object, no additional text before or after.
"""
        
        completion = model_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        # Extract JSON from response
        try:
            # Try to find JSON in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            wireframe_data = json.loads(response_text)
            
            response = {
                "title": wireframe_data.get("title", "UI/UX Wireframe"),
                "wireframe_type": wireframe_data.get("wireframe_type", "low-fidelity"),
                "screens": wireframe_data.get("screens", ""),
                "layout_structure": wireframe_data.get("layout_structure", ""),
                "components": wireframe_data.get("components", ""),
                "navigation_flow": wireframe_data.get("navigation_flow", ""),
                "annotations": wireframe_data.get("annotations", ""),
                "responsive_behavior": wireframe_data.get("responsive_behavior", ""),
                "detail": wireframe_data.get("detail", response_text)
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            # Fallback response
            response = {
                "title": "UI/UX Wireframe",
                "wireframe_type": "low-fidelity",
                "screens": "Wireframe screens generated",
                "layout_structure": "Standard grid layout",
                "components": "Common UI components",
                "navigation_flow": "Standard navigation",
                "annotations": "Design notes",
                "responsive_behavior": "Responsive design",
                "detail": response_text
            }
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error generating wireframe: {str(e)}")
        return {
            "response": {
                "title": "Error generating wireframe",
                "wireframe_type": "error",
                "screens": "",
                "layout_structure": "",
                "components": "",
                "navigation_flow": "",
                "annotations": "",
                "responsive_behavior": "",
                "detail": f"Error: {str(e)}"
            }
        }


# Build workflow graph
workflow = StateGraph(UIUXWireframeState)

# Add nodes
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_uiux_wireframe", generate_uiux_wireframe)

# Define edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_uiux_wireframe")
workflow.add_edge("generate_uiux_wireframe", END)

# Compile graph
uiux_wireframe_graph = workflow.compile()
