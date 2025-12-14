# workflows/usecase_diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.diagram import DiagramOutput, DiagramResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
import re
import logging
from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager

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

def generate_usecase_diagram_description(state: UsecaseDiagramState) -> UsecaseDiagramState:
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

    Create a detailed UML Use Case Diagram in Mermaid markdown format based on the requirement: {user_message}

    The diagram should include:
    - System boundary (the system being modeled)
    - Actors (external entities interacting with the system):
      * Primary actors (directly interact with the system)
      * Secondary actors (support the system)
      * Actor types: User, Administrator, External System, etc.
    - Use cases (functionalities provided by the system):
      * Use case name (verb + noun format, e.g., "Create Account", "Process Payment")
      * Brief description of what each use case does
    - Relationships between use cases:
      * Include relationship (one use case includes another)
      * Extend relationship (optional behavior)
      * Generalization (inheritance between actors or use cases)
    - Associations between actors and use cases (which actors interact with which use cases)
    - Key scenarios or user flows

    IMPORTANT: Return ONLY the Mermaid markdown code block for the use case diagram, starting with ```mermaid and ending with ```.
    Do not include any explanatory text before or after the code block.

    Example format:
    ```mermaid
    graph TD
        Actor1[Actor Name]
        UseCase1((Use Case Name))
        Actor1 --> UseCase1
    ```
    """

    try:
        completion = model_client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL
        )

        markdown_diagram = completion.choices[0].message.content

        # Create response with diagram type and markdown detail
        diagram_response = DiagramResponse(
            type="usecase_diagram",
            detail=markdown_diagram
        )
        output = DiagramOutput(type="diagram", response=diagram_response)

        return {"response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error generating use case diagram: {e}")
        # Fallback response
        return {
            "response": {
                "type": "usecase_diagram",
                "detail": f"Error generating use case diagram: {str(e)}"
            }
        }
      
def extract_mermaid_code(markdown_text: str) -> str:
    """Extract mermaid code from markdown fenced code block"""
    pattern = r'```mermaid\s*\n(.*?)```'
    match = re.search(pattern, markdown_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return markdown_text.strip()

def validate_diagram(state: UsecaseDiagramState) -> UsecaseDiagramState:
    """Validate the generated mermaid diagram"""
    raw_diagram = state.get("raw_diagram", "")
    if not raw_diagram:
        logger.error("No diagram to validate")
        return {
            "validation_result": {"valid": False, "errors": ["No diagram generated"]}
        }
    
    # Extract mermaid code from markdown
    mermaid_code = extract_mermaid_code(raw_diagram)
    
    validator = MermaidSubprocessManager()
    try:
        result = validator.validate_sync(mermaid_code)
        logger.info(f"Validation result: {result.get('valid', False)}")
        return {"validation_result": result}
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return {
            "validation_result": {"valid": False, "errors": [str(e)]}
        }
    finally:
        validator.sync_client.close()

def finalize_response(state: UsecaseDiagramState) -> UsecaseDiagramState:
    """Create final response based on validation result"""
    validation_result = state.get("validation_result", {})
    raw_diagram = state.get("raw_diagram", "")
    
    if validation_result.get("valid", False):
        # Validation passed
        diagram_response = DiagramResponse(
            type="usecase_diagram",
            detail=raw_diagram
        )
        output = DiagramOutput(type="diagram", response=diagram_response)
        return {"response": output.model_dump()["response"]}
    else:
        # Validation failed - still return the diagram but log the error
        errors = validation_result.get("errors", [])
        logger.warning(f"Usecase diagram validation failed: {errors}")
        
        # Return diagram anyway with a warning in the metadata
        diagram_response = DiagramResponse(
            type="usecase_diagram",
            detail=raw_diagram + f"\n\n<!-- Validation Warning: {errors} -->"
        )
        output = DiagramOutput(type="diagram", response=diagram_response)
        return {"response": output.model_dump()["response"]}

def extract_mermaid_code(markdown_text: str) -> str:
    """Extract mermaid code from markdown fenced code block"""
    pattern = r'```mermaid\s*\n(.*?)```'
    match = re.search(pattern, markdown_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return markdown_text.strip()

def validate_diagram(state: UsecaseDiagramState) -> UsecaseDiagramState:
    """Validate the generated mermaid diagram"""
    raw_diagram = state.get("raw_diagram", "")
    if not raw_diagram:
        logger.error("No diagram to validate")
        return {
            "validation_result": {"valid": False, "errors": ["No diagram generated"]}
        }
    
    # Extract mermaid code from markdown
    mermaid_code = extract_mermaid_code(raw_diagram)
    
    validator = MermaidSubprocessManager()
    try:
        result = validator.validate_sync(mermaid_code)
        logger.info(f"Validation result: {result.get('valid', False)}")
        return {"validation_result": result}
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return {
            "validation_result": {"valid": False, "errors": [str(e)]}
        }
    finally:
        validator.sync_client.close()

def finalize_response(state: UsecaseDiagramState) -> UsecaseDiagramState:
    """Create final response based on validation result"""
    validation_result = state.get("validation_result", {})
    raw_diagram = state.get("raw_diagram", "")
    
    if validation_result.get("valid", False):
        # Validation passed
        diagram_response = DiagramResponse(
            type="usecase_diagram",
            detail=raw_diagram
        )
        output = DiagramOutput(type="diagram", response=diagram_response)
        return {"response": output.model_dump()["response"]}
    else:
        # Validation failed - still return the diagram but log the error
        errors = validation_result.get("errors", [])
        logger.warning(f"Usecase diagram validation failed: {errors}")
        
        # Return diagram anyway with a warning in the metadata
        diagram_response = DiagramResponse(
            type="usecase_diagram",
            detail=raw_diagram + f"\n\n<!-- Validation Warning: {errors} -->"
        )
        output = DiagramOutput(type="diagram", response=diagram_response)
        return {"response": output.model_dump()["response"]}

# Build LangGraph pipeline for Use Case Diagram
workflow = StateGraph(UsecaseDiagramState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_usecase_diagram", generate_usecase_diagram_description)
workflow.add_node("validate_diagram", validate_diagram)
workflow.add_node("finalize_response", finalize_response)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_usecase_diagram")
workflow.add_edge("generate_usecase_diagram", "validate_diagram")
workflow.add_edge("validate_diagram", "finalize_response")
workflow.add_edge("finalize_response", END)

# Compile graph
usecase_diagram_graph = workflow.compile()