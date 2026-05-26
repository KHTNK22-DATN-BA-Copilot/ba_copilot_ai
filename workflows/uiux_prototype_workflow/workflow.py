"""
UI/UX Prototype Workflow for Phase 6 - UI/UX Design Phase
Generates interactive prototype specifications and user flow documentation
"""

from langgraph.graph import StateGraph, END
from typing import Optional, List, Dict
import json
import logging
from connect_model import get_model_client, set_request_model_config, reset_request_model_config, MODEL
from utils import extractor
from response import success_response, error_response
from models import UIUXPrototypeState

logger = logging.getLogger(__name__)


def get_context_node(state: UIUXPrototypeState) -> UIUXPrototypeState:
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
        return {"chat_context": []}
    
    # TODO: Implement chat history retrieval from database
    return {"chat_context": []}


def generate_uiux_prototype(state: UIUXPrototypeState, config: Optional[dict] = None):
    """
    Generate interactive prototype specifications and user flow documentation
    """
    model_client = get_model_client()
    cfg = (config or {}).get("configurable", {})
    token = set_request_model_config(
        provider=cfg.get("provider"),
        model_name=cfg.get("model_name"),
        api_key=cfg.get("api_key"),
    )
    try:
        
        user_message = state.get('message', '')
        extracted_text = state.get('extracted_text', '')
        chat_context = state.get('chat_context') or []

        prompt = f"""
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
        
        messages: List[dict] = [
            {"role": "system", "content": prompt},
            *chat_context,
        ]
        if extracted_text:
            messages.append({"role": "assistant", "content": extracted_text})
        messages.append({"role": "user", "content": user_message})

        response = model_client.chat_completion(
            messages=messages,
            model=cfg.get("model_name") or MODEL,
        )
        raw_output = response.choices[0].message.content or ""

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
            "response": success_response(summary, content)
        } # pyright: ignore[reportReturnType]
    except json.JSONDecodeError as e:
        logger.error(f"Error generating UIUX Prototype: {e}")
        return {
            "response": error_response("UIUX Prototype", f"Error generating UIUX Prototype: {e}")
        } # pyright: ignore[reportReturnType]
    finally:
        reset_request_model_config(token)

# Build workflow graph
workflow = StateGraph(UIUXPrototypeState)

# Add nodes
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_uiux_prototype", generate_uiux_prototype)

# Define edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_uiux_prototype")
workflow.add_edge("generate_uiux_prototype", END)

# Compile graph
uiux_prototype_graph = workflow.compile()
