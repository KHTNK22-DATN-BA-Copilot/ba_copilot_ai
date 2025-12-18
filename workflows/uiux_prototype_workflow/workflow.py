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
        
        prompt = f"""{context_str}

You are an expert Interaction Designer specializing in interactive prototypes. Create comprehensive prototype specifications for:

{user_message}

Generate a detailed prototype specification that includes:
1. Title and prototype type (interactive, clickable, animated)
2. Primary user flows and journeys
3. Interaction patterns (click, hover, scroll, swipe, drag)
4. Animations and transitions (micro-interactions, page transitions)
5. UI states for all components (default, hover, active, disabled, error, loading)
6. Use case scenarios covered by the prototype
7. Accessibility features (WCAG compliance, keyboard navigation, screen reader support)
8. Usability testing guidelines and scenarios
9. Complete prototype specification

Return ONLY a valid JSON object with this exact structure:
{{
  "title": "Prototype title",
  "prototype_type": "interactive or clickable or animated",
  "user_flows": "Flow 1: Login -> Dashboard -> Profile. Flow 2: Browse Products -> Add to Cart -> Checkout",
  "interactions": "Click: Navigate to page. Hover: Show tooltip. Scroll: Reveal content. Swipe: Navigate carousel",
  "animations": "Page transitions: 300ms fade. Button hover: Scale 1.05 with 200ms ease. Loading: Skeleton screens",
  "states": "Button states: default (blue), hover (darker blue), active (pressed), disabled (gray), loading (spinner)",
  "scenarios": "Scenario 1: First-time user registration. Scenario 2: Returning user purchase. Scenario 3: Error recovery",
  "accessibility": "WCAG 2.1 AA compliant, keyboard navigation, ARIA labels, focus indicators, screen reader tested",
  "testing_notes": "Test with 5 users, task completion rate, time on task, error rate, satisfaction score",
  "detail": "Complete prototype specification with all interaction details"
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
            
            prototype_data = json.loads(response_text)
            
            response = {
                "title": prototype_data.get("title", "UI/UX Prototype"),
                "prototype_type": prototype_data.get("prototype_type", "interactive"),
                "user_flows": prototype_data.get("user_flows", ""),
                "interactions": prototype_data.get("interactions", ""),
                "animations": prototype_data.get("animations", ""),
                "states": prototype_data.get("states", ""),
                "scenarios": prototype_data.get("scenarios", ""),
                "accessibility": prototype_data.get("accessibility", ""),
                "testing_notes": prototype_data.get("testing_notes", ""),
                "detail": prototype_data.get("detail", response_text)
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            # Fallback response
            response = {
                "title": "UI/UX Prototype",
                "prototype_type": "interactive",
                "user_flows": "User flows documented",
                "interactions": "Interactive elements defined",
                "animations": "Transitions specified",
                "states": "UI states included",
                "scenarios": "Use cases covered",
                "accessibility": "Accessibility considered",
                "testing_notes": "Testing guidelines provided",
                "detail": response_text
            }
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error generating prototype: {str(e)}")
        return {
            "response": {
                "title": "Error generating prototype",
                "prototype_type": "error",
                "user_flows": "",
                "interactions": "",
                "animations": "",
                "states": "",
                "scenarios": "",
                "accessibility": "",
                "testing_notes": "",
                "detail": f"Error: {str(e)}"
            }
        }


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
