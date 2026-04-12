# workflows/usecase_diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from models.diagram import DiagramOutput, DiagramResponse
# from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
import logging
from ..utils import extractor

logger = logging.getLogger(__name__)

class UsecaseDiagramState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]
    raw_diagram: Optional[str]
    validation_result: Optional[dict]
    retry_count: int

def generate_usecase_diagram_description(state: UsecaseDiagramState):
    """Generate use-case diagram in markdown format using OpenRouter AI"""
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
    Expert UML Use Case Diagram Designer (Mermaid).

    ### TASK
    Create a UML Use Case Diagram for: {user_message}

    ### REQUIREMENTS
    - Use Mermaid flowchart (graph TD or TB)
    - Include:
    - System boundary (labeled)
    - Actors (primary, secondary; e.g., User, Admin, External System)
    - Use cases (verb + noun naming)
    - Associations (actor ↔ use case)
    - Relationships:
        - include
        - extend
        - generalization
    - Group elements clearly (e.g., system boundary via subgraph)
    - Ensure logical structure and readability

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Mermaid diagram starting with 'graph TD' or 'graph TB' (with backticks, use \\n for newlines)",
    "summary": "One-line use case summary"
    }}

    ### RULES
    - Do include ``` as markdown wrappers
    - Escape \\n properly
    - No extra keys, no extra text
    - Must be valid JSON (parsable)
    - Use valid Mermaid syntax only
    """

    try:
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
        summary = "Use Case Diagram"
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "Use Case Diagram")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating use case diagram: {e}")

# def validate_diagram(state: UsecaseDiagramState) -> UsecaseDiagramState:
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

# def finalize_response(state: UsecaseDiagramState) -> UsecaseDiagramState:
#     """Create final response based on validation result"""
#     validation_result = state.get("validation_result", {})
#     raw_diagram = state.get("raw_diagram", "")
    
#     if validation_result.get("valid", False):
#         # Validation passed
#         diagram_response = DiagramResponse(
#             type="usecase_diagram",
#             detail=raw_diagram
#         )
#         output = DiagramOutput(type="diagram", response=diagram_response)
#         return {"response": output.model_dump()["response"]}
#     else:
#         # Validation failed - still return the diagram but log the error
#         errors = validation_result.get("errors", [])
#         logger.warning(f"Usecase diagram validation failed: {errors}")
        
#         # Return diagram anyway with a warning in the metadata
#         diagram_response = DiagramResponse(
#             type="usecase_diagram",
#             detail=raw_diagram + f"\n\n<!-- Validation Warning: {errors} -->"
#         )
#         output = DiagramOutput(type="diagram", response=diagram_response)
#         return {"response": output.model_dump()["response"]}

# def validate_diagram(state: UsecaseDiagramState) -> UsecaseDiagramState:
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

# def finalize_response(state: UsecaseDiagramState) -> UsecaseDiagramState:
#     """Create final response based on validation result"""
#     validation_result = state.get("validation_result", {})
#     raw_diagram = state.get("raw_diagram", "")
    
#     if validation_result.get("valid", False):
#         # Validation passed
#         diagram_response = DiagramResponse(
#             type="usecase_diagram",
#             detail=raw_diagram
#         )
#         output = DiagramOutput(type="diagram", response=diagram_response)
#         return {"response": output.model_dump()["response"]}
#     else:
#         # Validation failed - still return the diagram but log the error
#         errors = validation_result.get("errors", [])
#         logger.warning(f"Usecase diagram validation failed: {errors}")
        
#         # Return diagram anyway with a warning in the metadata
#         diagram_response = DiagramResponse(
#             type="usecase_diagram",
#             detail=raw_diagram + f"\n\n<!-- Validation Warning: {errors} -->"
#         )
#         output = DiagramOutput(type="diagram", response=diagram_response)
#         return {"response": output.model_dump()["response"]}

# Build LangGraph pipeline for Use Case Diagram
workflow = StateGraph(UsecaseDiagramState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_usecase_diagram", generate_usecase_diagram_description)
# workflow.add_node("validate_diagram", validate_diagram)
# workflow.add_node("finalize_response", finalize_response)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_usecase_diagram")
# workflow.add_edge("generate_usecase_diagram", "validate_diagram")
# workflow.add_edge("validate_diagram", "finalize_response")
# workflow.add_edge("finalize_response", END)
workflow.add_edge("generate_usecase_diagram", END)

# Compile graph
usecase_diagram_graph = workflow.compile()