"""
UI/UX Mockup Workflow for Phase 6 - UI/UX Design Phase
Generates high-fidelity UI mockups with design specifications
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict
import json
import logging
from connect_model import get_model_client, MODEL

logger = logging.getLogger(__name__)


class UIUXMockupState(TypedDict):
    """State for mockup generation workflow"""
    message: str
    content_id: Optional[str]
    storage_paths: Optional[List[str]]
    response: Optional[Dict]
    extracted_text: Optional[str]
    chat_context: Optional[str]


def get_content_file(state: UIUXMockupState) -> UIUXMockupState:
    """Extract content from uploaded files"""
    storage_paths = state.get('storage_paths')
    
    if not storage_paths:
        print("No storage_paths provided, skipping file content retrieval")
        return {"extracted_text": ""}
    
    # TODO: Implement file extraction from Supabase Storage
    return {"extracted_text": ""}


def get_chat_history(state: UIUXMockupState) -> UIUXMockupState:
    """Retrieve chat history from content_id"""
    content_id = state.get('content_id')
    
    if not content_id:
        print("No content_id provided, skipping chat history")
        return {"chat_context": ""}
    
    # TODO: Implement chat history retrieval from database
    return {"chat_context": ""}


def generate_uiux_mockup(state: UIUXMockupState) -> UIUXMockupState:
    """
    Generate high-fidelity UI/UX mockup with design specifications
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
        You are an expert Visual Designer and Frontend Engineer specializing in high-fidelity UI mockups using pure HTML and CSS.

        ### TASK
        Create a detailed visual mockup for the following request:

        {user_message}

        ### REQUIREMENTS
        Design a modern, clean with a focus on structure, typography over colors. Ensure UI following professional design principles, best practices.

        Include:
        1. Clear page structure and layout
        2. Visual hierarchy
        3. Consistent spacing system
        4. Modern color palette
        5. Typography hierarchy
        6. UI components (buttons, cards, forms if relevant)
        7. Responsive-friendly layout structure

        ### DESIGN GUIDELINES
        - Use semantic HTML elements (header, main, section, nav, footer).
        - Use clean class naming.
        - Follow modern UI design practices.
        - Ensure good visual hierarchy.
        - Use a minimal but professional color palette.
        - Ensure layout clarity and readable spacing.

        ### OUTPUT RULES
        Return ONLY a valid JSON object.

        Do NOT include:
        - explanations
        - markdown
        - comments
        - code blocks

        The JSON must contain exactly two keys:
        - "html"
        - "css"

        ### HTML RULES
        - Entire HTML must be on ONE LINE.
        - Use single quotes for HTML attributes.
        - Do NOT include <style> tags.

        ### CSS RULES
        - Entire CSS must be on ONE LINE.
        - Do not include comments.
        - Only pure CSS.

        ### JSON ESCAPING RULES
        - Escape all double quotes inside JSON strings.
        - Do not include line breaks.
        - Ensure valid JSON syntax.

        ### REQUIRED OUTPUT FORMAT
        {{
        "html": "<!DOCTYPE html><html><head><title>Mockup</title></head><body><header class='header'><h1>Product</h1></header><main class='container'><section class='hero'><h2>Main heading</h2><p>Supporting text</p><button class='btn-primary'>Get Started</button></section></main><footer class='footer'><p>©2026</p></footer></body></html>",
        "css": "body{{margin:0;font-family:Arial,sans-serif;background:#f8f9fb;color:#222;}} .container{{max-width:1100px;margin:0 auto;padding:40px;}} .hero{{text-align:center;padding:60px 0;}} .btn-primary{{background:#4f46e5;color:white;border:none;padding:12px 20px;border-radius:6px;cursor:pointer;}} .header{{padding:20px;border-bottom:1px solid #eee;}} .footer{{text-align:center;padding:30px;border-top:1px solid #eee;color:#777;}}"
        }}
        """
        
        completion = model_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL
        )
        response_text = completion.choices[0].message.content.strip()
        # remove markdown fences if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        parsed = json.loads(response_text)
        return {"type": "uiux_mockup", "response": {"html": parsed.get("html", ""), "css": parsed.get("css", "")}}
        
    except json.JSONDecodeError as e:
        logger.error(f"Error generating UIUX Mockup: {e}")
        raise e


# Build workflow graph
workflow = StateGraph(UIUXMockupState)

# Add nodes
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_uiux_mockup", generate_uiux_mockup)

# Define edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_uiux_mockup")
workflow.add_edge("generate_uiux_mockup", END)

# Compile graph
uiux_mockup_graph = workflow.compile()
