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
        
        prompt = f"""{context_str}
        
        ### ROLE
        You are an expert Visual Designer specializing in high-fidelity UI mockups. With deep knowledge of design systems, typography, color theory, and user interface principles.
        
        ### CONTEXT
        Create comprehensive UI/UX mockup specifications for:
        
        {user_message}
        
        Generate a detailed mockup that includes:
        1. Title and mockup type (visual-design, high-fidelity, pixel-perfect)
        2. Design system guidelines (colors, typography, spacing)
        3. Visual hierarchy principles
        4. Complete color palette with hex codes (primary, secondary, accent, neutrals)
        5. Typography specifications (font families, sizes, weights, line heights)
        6. Iconography style and set
        7. Imagery and photography style
        8. UI element specifications (buttons, forms, cards, etc.)
        9. Complete mockup specification
        
        ### INSTRUCTIONS
        1. Read and analyze the context in {context_str} and **<CONTEXT** section above.
        2. Create a detailed UI/UX mockup specification covering all specified sections.
        3. Ensure clarity, completeness, and correctness in the document.
        
        ### NOTE
        1. Use JSON format for the mockup specification.
        2. Follow best practices for UI/UX design documentation.
        3. Ensure the JSON is well-formed and valid.
        
        ### EXAMPLE OUTPUT
        Return ONLY a valid JSON object with this exact structure:
        {{
          "title": "Mockup title",
          "mockup_type": "visual-design or high-fidelity or pixel-perfect",
          "design_system": "Design system overview and guidelines",
          "visual_hierarchy": "Typography hierarchy, visual weight, spacing rhythm",
          "color_palette": "Primary: #1A73E8, Secondary: #34A853, Accent: #FBBC04, Error: #EA4335, Success: #34A853, Neutral-900: #202124, Neutral-50: #F8F9FA",
          "typography": "Headings: Inter Bold 32px/40px, Body: Inter Regular 16px/24px, etc.",
          "iconography": "Material Icons, 24px, outlined style",
          "imagery_style": "Flat illustrations, vibrant colors, modern minimalist photography",
          "ui_elements": "Primary button: 48px height, 16px padding, #1A73E8 background, white text, 4px border-radius",
          "detail": "Complete mockup specification with all visual details"
        }}
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
            
            mockup_data = json.loads(response_text)
            
            response = {
                "title": mockup_data.get("title", "UI/UX Mockup"),
                "mockup_type": mockup_data.get("mockup_type", "high-fidelity"),
                "design_system": mockup_data.get("design_system", ""),
                "visual_hierarchy": mockup_data.get("visual_hierarchy", ""),
                "color_palette": mockup_data.get("color_palette", ""),
                "typography": mockup_data.get("typography", ""),
                "iconography": mockup_data.get("iconography", ""),
                "imagery_style": mockup_data.get("imagery_style", ""),
                "ui_elements": mockup_data.get("ui_elements", ""),
                "detail": mockup_data.get("detail", response_text)
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            # Fallback response
            response = {
                "title": "UI/UX Mockup",
                "mockup_type": "high-fidelity",
                "design_system": "Modern design system",
                "visual_hierarchy": "Clear visual hierarchy",
                "color_palette": "Brand colors applied",
                "typography": "System fonts",
                "iconography": "Icon set included",
                "imagery_style": "Professional imagery",
                "ui_elements": "Consistent UI elements",
                "detail": response_text
            }
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error generating mockup: {str(e)}")
        return {
            "response": {
                "title": "Error generating mockup",
                "mockup_type": "error",
                "design_system": "",
                "visual_hierarchy": "",
                "color_palette": "",
                "typography": "",
                "iconography": "",
                "imagery_style": "",
                "ui_elements": "",
                "detail": f"Error: {str(e)}"
            }
        }


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
