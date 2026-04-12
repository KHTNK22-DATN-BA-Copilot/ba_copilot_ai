"""
UI/UX Wireframe Workflow for Phase 6 - UI/UX Design Phase
Generates UI wireframes with layout and component specifications
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict
import json
import logging
from connect_model import get_model_client, MODEL
from ..utils import extractor

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
        
        prompt = f"""
        {context_str}

        ### ROLE
        UX/UI Wireframe Designer (HTML/CSS Layout).

        ### TASK
        Create a structured UI wireframe for: {user_message}

        ### REQUIREMENTS
        - Define layout structure using semantic HTML (header, nav, main, section, footer)
        - Show layout hierarchy and content grouping
        - Include navigation, hero, content sections, and at least 1 form
        - Use grid/flex for layout
        - Include responsive behavior (mobile breakpoint)
        - Focus on structure, NOT visual styling

        ### OUTPUT (STRICT JSON ONLY)
        {{
        "content": {{
            "html": "<single-line HTML>",
            "css": "<single-line CSS>"
        }},
        "summary": "One-line description of layout"
        }}

        ### RULES
        - Return ONLY valid JSON
        - No markdown, no explanations
        - No extra or missing keys
        - HTML & CSS MUST NOT be empty
        - HTML & CSS must be single-line strings
        - Use single quotes in HTML
        - Do NOT include <style> tags
        - No comments in CSS
        - Include responsive layout (@media)
        - Escape quotes properly
        - Ensure JSON is parsable

        ### FALLBACK
        - If unsure, still generate a basic but complete wireframe
        - NEVER return empty html or css
        """
        
        # Use Open Router (default)
        # completion = model_client.chat_completion(
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": prompt
        #         }
        #     ],
        #     model=MODEL
        # )
        # raw_output = completion.choices[0].message.content

        # Use Gemini 2.5 Flash Lite
        raw_output = model_client.gemini_completion(prompt)

        json_data = extractor.extract_json(raw_output)
        summary = "UIUX Wireframe"
        content = "No content"
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "UIUX Wireframe")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
        
    except json.JSONDecodeError as e:
        logger.error(f"Error generating UIUX Wireframe: {e}")
        raise e

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
