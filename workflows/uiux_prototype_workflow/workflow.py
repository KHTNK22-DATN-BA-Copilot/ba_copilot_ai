"""
UI/UX Prototype Workflow for Phase 6 - UI/UX Design Phase
Generates interactive prototype specifications and user flow documentation
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict
import json
import logging
from connect_model import get_model_client, MODEL
from ..utils import extractor

logger = logging.getLogger(__name__)


class UIUXPrototypeState(TypedDict):
    """State for prototype generation workflow"""
    message: str
    content_id: Optional[str]
    storage_paths: Optional[List[str]]
    response: Optional[Dict]
    extracted_text: Optional[str]
    chat_context: Optional[str]


def get_content_file(state: UIUXPrototypeState) -> UIUXPrototypeState:
    """Extract content from uploaded files"""
    storage_paths = state.get('storage_paths')
    
    if not storage_paths:
        print("No storage_paths provided, skipping file content retrieval")
        return {"extracted_text": ""}
    
    # TODO: Implement file extraction from Supabase Storage
    return {"extracted_text": ""}


def get_chat_history(state: UIUXPrototypeState) -> UIUXPrototypeState:
    """Retrieve chat history from content_id"""
    content_id = state.get('content_id')
    
    if not content_id:
        print("No content_id provided, skipping chat history")
        return {"chat_context": ""}
    
    # TODO: Implement chat history retrieval from database
    return {"chat_context": ""}


def generate_uiux_prototype(state: UIUXPrototypeState):
    """
    Generate interactive prototype specifications and user flow documentation
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
        Interaction Designer & Frontend Prototyper (HTML/CSS).

        ### TASK
        Create an interactive UI prototype for: {user_message}

        ### REQUIREMENTS
        - Demonstrate:
        - Page structure (header, nav, main, sections, footer)
        - Navigation flow and layout hierarchy
        - Interaction states (hover, focus, active)
        - Responsive behavior (mobile, tablet, desktop)
        - At least 3 interactive components (e.g., nav, cards, form, modal)
        - Use semantic HTML and clear class naming
        - Use CSS for layout, responsiveness (media queries), and interactions
        - Follow modern UX principles (clarity, accessibility, spacing)

        ### OUTPUT (STRICT JSON ONLY)
        {{
        "content": {{
            "html": "<single-line HTML>",
            "css": "<single-line CSS>"
        }},
        "summary": "One-line prototype description"
        }}

        ### RULES
        - Output JSON ONLY (no markdown, no explanations)
        - No extra keys, no missing keys
        - HTML & CSS must be single-line strings
        - Use single quotes for HTML attributes
        - Do NOT include <style> tags
        - No comments in CSS
        - Include responsive + interaction states
        - Escape quotes properly
        - Ensure valid JSON (parsable)
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
        summary = "UIUX Prototype"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "UIUX Prototype")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except json.JSONDecodeError as e:
        logger.error(f"Error generating UIUX Prototype: {e}")

# Build workflow graph
workflow = StateGraph(UIUXPrototypeState)

# Add nodes
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_uiux_prototype", generate_uiux_prototype)

# Define edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_uiux_prototype")
workflow.add_edge("generate_uiux_prototype", END)

# Compile graph
uiux_prototype_graph = workflow.compile()
