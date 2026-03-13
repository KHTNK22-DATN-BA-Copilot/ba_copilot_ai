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
        
        prompt = f"""
        {context_str}

        ### ROLE
        You are an expert UX/UI Designer and Layout Architect specializing in wireframe systems and structured UI layouts using pure HTML and CSS.

        You focus on:
        - page architecture
        - information hierarchy
        - layout systems
        - component placement
        - responsive structure

        ### TASK
        Create a **comprehensive UI wireframe layout** for:

        {user_message}

        The wireframe should represent the **overall product structure**, including layout hierarchy, navigation structure, and major UI sections.

        This wireframe may incorporate ideas from mockups and prototypes but should primarily focus on **layout architecture and screen structure**.

        ### WIREFRAME OBJECTIVES
        Design a structured wireframe that demonstrates:

        1. Overall page layout
        2. Screen or section hierarchy
        3. Information architecture
        4. Navigation structure
        5. Placement of UI components
        6. Responsive layout structure
        7. Clear visual hierarchy
        8. Logical grouping of content areas

        ### DESIGN GUIDELINES
        Follow professional UX layout principles:

        - grid-based layout
        - consistent spacing system
        - strong visual hierarchy
        - clear content grouping
        - intuitive navigation
        - scalable component placement

        ### LAYOUT STRUCTURE GUIDELINES
        Use a modern layout structure such as:

        - max-width container
        - grid or flex layout
        - section-based page structure
        - clear header / main / footer separation

        Typical wireframe sections may include:

        - header navigation
        - hero or page introduction
        - feature sections
        - content blocks
        - cards or lists
        - form areas
        - call-to-action sections
        - footer navigation

        ### HTML STRUCTURE GUIDELINES
        Use semantic HTML elements when possible:

        header  
        nav  
        main  
        section  
        article  
        aside  
        footer  

        Ensure the layout clearly represents **wireframe structure and page hierarchy**.

        ### CSS STRUCTURE GUIDELINES
        CSS should demonstrate:

        - layout system (grid/flex)
        - spacing scale
        - typography hierarchy
        - responsive breakpoints
        - visual grouping
        - basic UI component structure

        The styling should reflect a **high-fidelity wireframe** (structured, readable, but not overly decorative).

        ### RESPONSIVE BEHAVIOR
        The wireframe must support multiple screen sizes:

        Mobile:
        - single-column layout

        Tablet:
        - two-column layout

        Desktop:
        - multi-column grid layout

        Use responsive CSS techniques such as:

        - flexible containers
        - grid layouts
        - media queries

        ### OUTPUT RULES
        Return ONLY a valid JSON object.

        Do NOT include:

        - explanations
        - markdown
        - comments
        - code blocks

        The JSON must contain exactly two fields:

        - "html"
        - "css"

        ### HTML RULES
        - Entire HTML must be on ONE LINE.
        - Use single quotes for HTML attributes.
        - Do NOT include <style> tags.
        - Structure must clearly represent a wireframe layout.

        ### CSS RULES
        - Entire CSS must be on ONE LINE.
        - Do not include comments.
        - Demonstrate layout system and responsive behavior.

        ### JSON ESCAPING RULES
        - Escape all double quotes inside JSON strings.
        - Do not include line breaks.
        - Ensure valid JSON syntax.

        ### REQUIRED OUTPUT FORMAT
        {{
        "html": "<!DOCTYPE html><html><head><title>Wireframe</title></head><body><header class='header'><nav class='nav'><div class='logo'>Brand</div><ul class='nav-links'><li><a href='#'>Home</a></li><li><a href='#'>Features</a></li><li><a href='#'>Pricing</a></li><li><a href='#'>Contact</a></li></ul></nav></header><main class='container'><section class='hero'><h1>Main Page Heading</h1><p>Introductory description for the product or service.</p><button class='cta'>Primary Action</button></section><section class='features'><article class='feature-card'><h3>Feature One</h3><p>Short description</p></article><article class='feature-card'><h3>Feature Two</h3><p>Short description</p></article><article class='feature-card'><h3>Feature Three</h3><p>Short description</p></article></section><section class='content'><div class='content-left'><h2>Content Area</h2><p>Supporting information block.</p></div><div class='content-right'><div class='card'>Secondary content</div></div></section><section class='form-section'><form class='form'><input class='input' placeholder='Email'><button class='submit'>Submit</button></form></section></main><footer class='footer'><p>Footer navigation and information</p></footer></body></html>",
        "css": "body{{margin:0;font-family:Arial,sans-serif;background:#fafafa;color:#222;}} .container{{max-width:1200px;margin:0 auto;padding:40px;}} .header{{border-bottom:1px solid #ddd;padding:16px;}} .nav{{display:flex;justify-content:space-between;align-items:center;}} .nav-links{{display:flex;gap:20px;list-style:none;margin:0;padding:0;}} .nav-links a{{text-decoration:none;color:#333;}} .hero{{padding:60px 0;text-align:center;}} .cta{{margin-top:20px;padding:12px 18px;border:none;background:#333;color:white;border-radius:6px;cursor:pointer;}} .features{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;margin-top:40px;}} .feature-card{{padding:20px;border:1px solid #ddd;border-radius:8px;background:white;}} .content{{display:grid;grid-template-columns:2fr 1fr;gap:30px;margin-top:40px;}} .card{{padding:20px;border:1px solid #ddd;border-radius:8px;background:white;}} .form-section{{margin-top:40px;text-align:center;}} .input{{padding:10px;border:1px solid #ccc;border-radius:4px;margin-right:10px;}} .submit{{padding:10px 16px;border:none;background:#111;color:white;border-radius:4px;}} .footer{{margin-top:60px;border-top:1px solid #ddd;padding:20px;text-align:center;color:#666;}} @media(max-width:768px){{.nav{{flex-direction:column;gap:10px;}} .content{{grid-template-columns:1fr;}} .hero{{padding:40px 10px;}}}}"
        }}
        """
        
        completion = model_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL
        )
        
        response_text = completion.choices[0].message.content.strip()
        return {"type": "uiux_wireframe_workflow", "response": response_text}
        # Extract JSON from response
    #     try:
    #         # Try to find JSON in markdown code blocks
    #         if "```json" in response_text:
    #             json_start = response_text.find("```json") + 7
    #             json_end = response_text.find("```", json_start)
    #             response_text = response_text[json_start:json_end].strip()
    #         elif "```" in response_text:
    #             json_start = response_text.find("```") + 3
    #             json_end = response_text.find("```", json_start)
    #             response_text = response_text[json_start:json_end].strip()
            
    #         wireframe_data = json.loads(response_text)
            
    #         response = {
    #             "title": wireframe_data.get("title", "UI/UX Wireframe"),
    #             "wireframe_type": wireframe_data.get("wireframe_type", "low-fidelity"),
    #             "screens": wireframe_data.get("screens", ""),
    #             "layout_structure": wireframe_data.get("layout_structure", ""),
    #             "components": wireframe_data.get("components", ""),
    #             "navigation_flow": wireframe_data.get("navigation_flow", ""),
    #             "annotations": wireframe_data.get("annotations", ""),
    #             "responsive_behavior": wireframe_data.get("responsive_behavior", ""),
    #             "detail": wireframe_data.get("detail", response_text)
    #         }
            
    #     except json.JSONDecodeError as e:
    #         logger.error(f"JSON parsing error: {e}")
    #         # Fallback response
    #         response = {
    #             "title": "UI/UX Wireframe",
    #             "wireframe_type": "low-fidelity",
    #             "screens": "Wireframe screens generated",
    #             "layout_structure": "Standard grid layout",
    #             "components": "Common UI components",
    #             "navigation_flow": "Standard navigation",
    #             "annotations": "Design notes",
    #             "responsive_behavior": "Responsive design",
    #             "detail": response_text
    #         }
        
    #     return {"response": response}
        
    # except Exception as e:
    #     logger.error(f"Error generating wireframe: {str(e)}")
    #     return {
    #         "response": {
    #             "title": "Error generating wireframe",
    #             "wireframe_type": "error",
    #             "screens": "",
    #             "layout_structure": "",
    #             "components": "",
    #             "navigation_flow": "",
    #             "annotations": "",
    #             "responsive_behavior": "",
    #             "detail": f"Error: {str(e)}"
    #         }
    #     }


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
