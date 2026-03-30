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
        You are an expert UX/UI Designer and Layout Architect specializing in wireframes and structured UI layouts using HTML and CSS.

        ### TASK
        Create a **comprehensive UI wireframe layout** for:

        {user_message}

        Focus on **page structure, layout hierarchy, navigation, and major UI sections**. This wireframe emphasizes layout architecture over styling or color details.

        ### OBJECTIVES
        - Overall page layout and section hierarchy
        - Information architecture and visual hierarchy
        - Navigation structure and content grouping
        - Responsive layout (mobile, tablet, desktop)
        - Placement of UI components (cards, forms, buttons, CTAs)

        ### GUIDELINES
        - Use semantic HTML: header, nav, main, section, article, aside, footer
        - Use grid/flex layout with a consistent spacing system
        - Demonstrate responsive behavior via media queries
        - CSS should reflect layout, spacing, typography, and component structure
        - Avoid decorative styling; focus on structure and readability

        ### OUTPUT RULES
        Return ONLY a valid JSON object with exactly two keys: `"html"` and `"css"`.

        - **HTML**: single line, single quotes for attributes, no `<style>` tags
        - **CSS**: single line, no comments, responsive and structured
        - Escape all quotes correctly for valid JSON
        - Do NOT include explanations, markdown, or extra text

        ### REQUIRED OUTPUT FORMAT
        {{
        "html": "<!DOCTYPE html><html><head><title>Wireframe</title></head><body><header class='header'><nav class='nav'><div class='logo'>Brand</div><ul class='nav-links'><li><a href='#'>Home</a></li><li><a href='#'>Features</a></li><li><a href='#'>Pricing</a></li><li><a href='#'>Contact</a></li></ul></nav></header><main class='container'><section class='hero'><h1>Main Heading</h1><p>Intro description</p><button class='cta'>Primary Action</button></section><section class='features'><article class='feature-card'><h3>Feature One</h3><p>Short description</p></article><article class='feature-card'><h3>Feature Two</h3><p>Short description</p></article><article class='feature-card'><h3>Feature Three</h3><p>Short description</p></article></section><section class='content'><div class='content-left'><h2>Content Area</h2><p>Supporting info</p></div><div class='content-right'><div class='card'>Secondary content</div></div></section><section class='form-section'><form class='form'><input class='input' placeholder='Email'><button class='submit'>Submit</button></form></section></main><footer class='footer'><p>Footer navigation</p></footer></body></html>",
        "css": "body{{margin:0;font-family:Arial,sans-serif;background:#fafafa;color:#222;}} .container{{max-width:1200px;margin:0 auto;padding:40px;}} .header{{border-bottom:1px solid #ddd;padding:16px;}} .nav{{display:flex;justify-content:space-between;align-items:center;}} .nav-links{{display:flex;gap:20px;list-style:none;margin:0;padding:0;}} .nav-links a{{text-decoration:none;color:#333;}} .hero{{padding:60px 0;text-align:center;}} .cta{{margin-top:20px;padding:12px 18px;border:none;background:#333;color:white;border-radius:6px;cursor:pointer;}} .features{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;margin-top:40px;}} .feature-card{{padding:20px;border:1px solid #ddd;border-radius:8px;background:white;}} .content{{display:grid;grid-template-columns:2fr 1fr;gap:30px;margin-top:40px;}} .card{{padding:20px;border:1px solid #ddd;border-radius:8px;background:white;}} .form-section{{margin-top:40px;text-align:center;}} .input{{padding:10px;border:1px solid #ccc;border-radius:4px;margin-right:10px;}} .submit{{padding:10px 16px;border:none;background:#111;color:white;border-radius:4px;}} .footer{{margin-top:60px;border-top:1px solid #ddd;padding:20px;text-align:center;color:#666;}} @media(max-width:768px){{.nav{{flex-direction:column;gap:10px;}} .content{{grid-template-columns:1fr;}} .hero{{padding:40px 10px;}}}}"
        }}
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
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "UIUX Wireframe")
            content = json_data.get("content", "")
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
