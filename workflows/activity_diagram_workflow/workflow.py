# workflows/activity_diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import re
import logging
from models.diagram import DiagramOutput, DiagramResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from ..utils import extractors

# from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager

logger = logging.getLogger(__name__)

class ActivityDiagramState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]
    raw_diagram: Optional[str]
    validation_result: Optional[dict]
    retry_count: int

def generate_activity_diagram_description(state: ActivityDiagramState):
    """Generate activity diagram in markdown format using OpenRouter AI"""
    model_client = get_model_client()

    # Build comprehensive prompt with context
    user_message = state['user_message']
    extracted_text = state.get('extracted_text', '')
    chat_context = state.get('chat_context', '')

    context_parts = []
    if chat_context:
        context_parts.append(f"Context from previous conversation:\n{chat_context}\n")
    if extracted_text:
        context_parts.append(f"Extracted content from uploaded files:\n{extracted_text}\n")

    context_str = "\n".join(context_parts)

    prompt = f"""
    {context_str}

    ### ROLE
    Expert UML Activity Diagram designer (Mermaid).

    ### TASK
    Create a UML Activity Diagram for: {user_message}

    ### REQUIREMENTS
    - Include: start/end, activities (verb + object), decisions (labeled), merges, flows
    - Add swimlanes and parallel flows if applicable
    - Ensure clear, logical structure
    - Mermaid syntax must be valid

    ### OUTPUT FORMAT (STRICT JSON)
    Return ONLY valid JSON (no markdown, no explanation):

    {{
    "content": "",
    "summary": ""
    }}

    ### RULES
    - "content" is mermaid diagram code starting and ending with backtick
    - "summary" is one-line concise description of the diagram
    - Escape newlines properly (\\n)
    - No extra keys
    - No extra text before/after JSON
    """

    try:
        # Using Open Router (default)
        # completion = model_client.chat_completion(
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": prompt
        #         }
        #     ],
        #     model=MODEL
        # )
        # raw_output = completion.choices[0].message.content or ""

        # Using Gemini 2.5 Flash lite
        raw_output = model_client.gemini_completion(prompt)
        
        json_data = extractors.extract_json(raw_output)
        summary = "Activity Diagram"
        content = ""
        if not json_data:
            logger.warning("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "Activity Diagram")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        logger.exception(f"Error generating product roadmap: {e}")

# def validate_diagram(state: ActivityDiagramState) -> ActivityDiagramState:
#     """Validate the generated mermaid diagram"""
#     raw_diagram = state.get("raw_diagram", "")
#     if not raw_diagram:
#         logger.error("No diagram to validate")
#         return {
#             "validation_result": {"valid": False, "errors": ["No diagram generated"]}
#         }
    
#     # Extract mermaid code from markdown
#     mermaid_code = extract_mermaid_code(raw_diagram)
    
#     validator = MermaidSubprocessManager()
#     try:
#         result = validator.validate_sync(mermaid_code)
#         logger.info(f"Validation result: {result.get('valid', False)}")
#         return {"validation_result": result}
#     except Exception as e:
#         logger.error(f"Validation failed: {e}")
#         return {
#             "validation_result": {"valid": False, "errors": [str(e)]}
#         }
#     finally:
#         validator.sync_client.close()

# def finalize_response(state: ActivityDiagramState) -> ActivityDiagramState:
#     """Create final response based on validation result"""
#     validation_result = state.get("validation_result", {})
#     raw_diagram = state.get("raw_diagram", "")
    
#     if validation_result.get("valid", False):
#         # Validation passed
#         diagram_response = DiagramResponse(
#             type="activity_diagram",
#             detail=raw_diagram
#         )
#         output = DiagramOutput(type="diagram", response=diagram_response)
#         return {"response": output.model_dump()["response"]}
#     else:
#         # Validation failed - still return the diagram but log the error
#         errors = validation_result.get("errors", [])
#         logger.warning(f"Activity diagram validation failed: {errors}")
        
#         # Return diagram anyway with a warning in the metadata
#         diagram_response = DiagramResponse(
#             type="activity_diagram",
#             detail=raw_diagram + f"\n\n<!-- Validation Warning: {errors} -->"
#         )
#         output = DiagramOutput(type="diagram", response=diagram_response)
#         return {"response": output.model_dump()["response"]}

# def extract_mermaid_code(markdown_text: str) -> str:
#     """Extract mermaid code from markdown fenced code block"""
#     pattern = r'```mermaid\s*\n(.*?)```'
#     match = re.search(pattern, markdown_text, re.DOTALL)
#     if match:
#         return match.group(1).strip()
#     return markdown_text.strip()

# def validate_diagram(state: ActivityDiagramState) -> ActivityDiagramState:
#     """Validate the generated mermaid diagram"""
#     raw_diagram = state.get("raw_diagram", "")
#     if not raw_diagram:
#         logger.error("No diagram to validate")
#         return {
#             "validation_result": {"valid": False, "errors": ["No diagram generated"]}
#         }
    
#     # Extract mermaid code from markdown
#     mermaid_code = extract_mermaid_code(raw_diagram)
    
#     validator = MermaidSubprocessManager()
#     try:
#         result = validator.validate_sync(mermaid_code)
#         logger.info(f"Validation result: {result.get('valid', False)}")
#         return {"validation_result": result}
#     except Exception as e:
#         logger.error(f"Validation failed: {e}")
#         return {
#             "validation_result": {"valid": False, "errors": [str(e)]}
#         }
#     finally:
#         validator.sync_client.close()

# def finalize_response(state: ActivityDiagramState) -> ActivityDiagramState:
#     """Create final response based on validation result"""
#     validation_result = state.get("validation_result", {})
#     raw_diagram = state.get("raw_diagram", "")
    
#     if validation_result.get("valid", False):
#         # Validation passed
#         diagram_response = DiagramResponse(
#             type="activity_diagram",
#             detail=raw_diagram
#         )
#         output = DiagramOutput(type="diagram", response=diagram_response)
#         return {"response": output.model_dump()["response"]}
#     else:
#         # Validation failed - still return the diagram but log the error
#         errors = validation_result.get("errors", [])
#         logger.warning(f"Activity diagram validation failed: {errors}")
        
#         # Return diagram anyway with a warning in the metadata
#         diagram_response = DiagramResponse(
#             type="activity_diagram",
#             detail=raw_diagram + f"\n\n<!-- Validation Warning: {errors} -->"
#         )
#         output = DiagramOutput(type="diagram", response=diagram_response)
#         return {"response": output.model_dump()["response"]}

# Build LangGraph pipeline for Activity Diagram
workflow = StateGraph(ActivityDiagramState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_activity_diagram", generate_activity_diagram_description)
# workflow.add_node("validate_diagram", validate_diagram)
# workflow.add_node("finalize_response", finalize_response)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_activity_diagram")
# workflow.add_edge("generate_activity_diagram", "validate_diagram")
# workflow.add_edge("validate_diagram", "finalize_response")
# workflow.add_edge("finalize_response", END)
workflow.add_edge("generate_activity_diagram", END)

# Compile graph
activity_diagram_graph = workflow.compile()