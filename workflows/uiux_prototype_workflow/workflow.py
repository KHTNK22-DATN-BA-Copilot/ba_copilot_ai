"""
UI/UX Prototype Workflow for Phase 6 - UI/UX Design Phase
Generates interactive prototype specifications and user flow documentation
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict
import json
import logging
from connect_model import get_model_client, MODEL

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


def generate_uiux_prototype(state: UIUXPrototypeState) -> UIUXPrototypeState:
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
        You are an expert Interaction Designer and Frontend Prototyper specializing in interactive UI prototypes built with pure HTML and CSS.

        You focus on:
        - interaction patterns
        - responsive layouts
        - page flows
        - UI states
        - usability testing prototypes

        ### TASK
        Create an **interactive UI prototype specification** for:

        {user_message}

        The output should represent a **clickable prototype structure** that demonstrates user navigation, layout behavior, and interaction states.

        ### PROTOTYPE OBJECTIVES
        Design a prototype that demonstrates:

        1. Page layout structure
        2. Navigation flow between sections/pages
        3. Interaction states (hover, focus, active)
        4. Responsive layout behavior
        5. Scroll interactions
        6. Component states (buttons, forms, cards)
        7. Clear visual hierarchy
        8. Accessibility considerations
        9. Page flow for usability testing

        ### DESIGN PRINCIPLES
        Follow modern UX principles:

        - mobile-first responsive layout
        - clear interaction affordances
        - consistent spacing system
        - accessible contrast and focus states
        - semantic HTML structure
        - intuitive navigation

        ### INTERACTION GUIDELINES
        Represent interactions using CSS states:

        Examples:
        - hover states
        - focus states
        - active states
        - expandable sections
        - navigation highlights
        - loading indicators
        - form validation styles

        ### RESPONSIVE GUIDELINES
        Prototype must support:

        - mobile layout
        - tablet layout
        - desktop layout

        Use CSS techniques such as:

        - flexible containers
        - responsive grids
        - media queries

        ### HTML STRUCTURE GUIDELINES
        Use semantic HTML elements when appropriate:

        header  
        nav  
        main  
        section  
        article  
        aside  
        footer  

        Include typical prototype sections such as:

        - navigation bar
        - hero section
        - content sections
        - cards or lists
        - forms or buttons
        - footer

        ### CSS STRUCTURE GUIDELINES
        CSS should demonstrate:

        - layout system
        - responsive behavior
        - interaction states
        - typography hierarchy
        - spacing scale
        - UI component styling

        ### OUTPUT RULES
        Return ONLY a valid JSON object.
        Ensure the prototype demonstrates at least 3 interactive components (nav menu, card hover, form interaction, expandable content, or modal).
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
        - Structure should represent an interactive prototype layout.

        ### CSS RULES
        - Entire CSS must be on ONE LINE.
        - Do not include comments.
        - Demonstrate responsive and interaction states.

        ### JSON ESCAPING RULES
        - Escape all double quotes inside JSON strings.
        - Do not include line breaks.
        - Ensure valid JSON syntax.

        ### REQUIRED OUTPUT FORMAT
        {{
        "html": "<!DOCTYPE html><html><head><title>Prototype</title></head><body><header class='header'><nav class='nav'><div class='logo'>Product</div><ul class='nav-links'><li><a href='#'>Home</a></li><li><a href='#'>Features</a></li><li><a href='#'>Pricing</a></li><li><a href='#'>Contact</a></li></ul></nav></header><main class='container'><section class='hero'><h1>Prototype Heading</h1><p>Introductory content explaining the prototype flow.</p><button class='btn-primary'>Start</button></section><section class='cards'><article class='card'><h3>Feature One</h3><p>Description</p></article><article class='card'><h3>Feature Two</h3><p>Description</p></article></section><section class='form-section'><form class='form'><input class='input' placeholder='Email'><button class='btn-submit'>Submit</button></form></section></main><footer class='footer'><p>Prototype Footer</p></footer></body></html>",
        "css": "body{{margin:0;font-family:Arial,sans-serif;background:#f5f6fa;color:#222;}} .container{{max-width:1100px;margin:0 auto;padding:40px;}} .header{{border-bottom:1px solid #eee;padding:16px;}} .nav{{display:flex;justify-content:space-between;align-items:center;}} .nav-links{{display:flex;gap:20px;list-style:none;margin:0;padding:0;}} .nav-links a{{text-decoration:none;color:#333;padding:6px 10px;border-radius:4px;}} .nav-links a:hover{{background:#f0f0f0;}} .hero{{text-align:center;padding:60px 0;}} .btn-primary{{background:#4f46e5;color:white;border:none;padding:12px 18px;border-radius:6px;cursor:pointer;transition:all .2s;}} .btn-primary:hover{{background:#4338ca;}} .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-top:40px;}} .card{{padding:20px;border:1px solid #eee;border-radius:8px;background:white;transition:transform .2s;}} .card:hover{{transform:translateY(-4px);}} .form-section{{margin-top:40px;text-align:center;}} .input{{padding:10px;border:1px solid #ccc;border-radius:4px;margin-right:10px;}} .btn-submit{{padding:10px 16px;background:#111;color:white;border:none;border-radius:4px;cursor:pointer;}} .footer{{margin-top:60px;text-align:center;padding:20px;border-top:1px solid #eee;}} @media(max-width:768px){{.nav{{flex-direction:column;gap:10px;}} .hero{{padding:40px 10px;}}}}"
        }}
        """
        
        completion = model_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL
        )
        
        response_text = completion.choices[0].message.content.strip()
        return {"type": "uiux_prototype_workflow", "response": response_text}
        # # Extract JSON from response
        # try:
        #     # Try to find JSON in markdown code blocks
        #     if "```json" in response_text:
        #         json_start = response_text.find("```json") + 7
        #         json_end = response_text.find("```", json_start)
        #         response_text = response_text[json_start:json_end].strip()
        #     elif "```" in response_text:
        #         json_start = response_text.find("```") + 3
        #         json_end = response_text.find("```", json_start)
        #         response_text = response_text[json_start:json_end].strip()
            
        #     prototype_data = json.loads(response_text)
            
        #     response = {
        #         "title": prototype_data.get("title", "UI/UX Prototype"),
        #         "prototype_type": prototype_data.get("prototype_type", "interactive"),
        #         "user_flows": prototype_data.get("user_flows", ""),
        #         "interactions": prototype_data.get("interactions", ""),
        #         "animations": prototype_data.get("animations", ""),
        #         "states": prototype_data.get("states", ""),
        #         "scenarios": prototype_data.get("scenarios", ""),
        #         "accessibility": prototype_data.get("accessibility", ""),
        #         "testing_notes": prototype_data.get("testing_notes", ""),
        #         "detail": prototype_data.get("detail", response_text)
        #     }
            
        # except json.JSONDecodeError as e:
        #     logger.error(f"JSON parsing error: {e}")
        #     # Fallback response
        #     response = {
        #         "title": "UI/UX Prototype",
        #         "prototype_type": "interactive",
        #         "user_flows": "User flows documented",
        #         "interactions": "Interactive elements defined",
        #         "animations": "Transitions specified",
        #         "states": "UI states included",
        #         "scenarios": "Use cases covered",
        #         "accessibility": "Accessibility considered",
        #         "testing_notes": "Testing guidelines provided",
        #         "detail": response_text
        #     }
        
        # return {"response": response}
        
    # except Exception as e:
    #     logger.error(f"Error generating prototype: {str(e)}")
    #     return {
    #         "response": {
    #             "title": "Error generating prototype",
    #             "prototype_type": "error",
    #             "user_flows": "",
    #             "interactions": "",
    #             "animations": "",
    #             "states": "",
    #             "scenarios": "",
    #             "accessibility": "",
    #             "testing_notes": "",
    #             "detail": f"Error: {str(e)}"
    #         }
    #     }


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
