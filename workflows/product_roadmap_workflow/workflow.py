# workflows/product_roadmap_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import re
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.product_roadmap import ProductRoadmapOutput, ProductRoadmapResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager

logger = logging.getLogger(__name__)

class ProductRoadmapState(TypedDict):
    user_message: Optional[str]
    response: Optional[dict]
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]
    raw_diagram: Optional[str]
    validation_result: Optional[dict]
    retry_count: int

def generate_product_roadmap_diagram(state: ProductRoadmapState) -> ProductRoadmapState:
    """Generate product roadmap Gantt diagram using OpenRouter AI"""
    model_client = get_model_client()

    # Build comprehensive prompt with context
    user_message = state.get('user_message', '')
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

    Create a detailed Product Roadmap as a Mermaid Gantt chart based on the following project:

    {user_message}

    The roadmap should include:
    - Project phases (Planning, Design, Development, Testing, Deployment)
    - Major milestones with specific dates
    - Dependencies between tasks
    - Timeline spanning multiple months/quarters
    - Key deliverables at each phase

    IMPORTANT: Return ONLY the Mermaid Gantt chart code block, starting with ```mermaid and ending with ```.
    Do not include any explanatory text before or after the code block.

    Example format:
    ```mermaid
    gantt
        title Product Roadmap
        dateFormat YYYY-MM-DD
        section Planning
        Requirements Gathering    :2024-01-01, 30d
        Stakeholder Interviews     :2024-01-15, 20d
        section Design
        System Architecture        :2024-02-01, 25d
        UI/UX Design              :2024-02-10, 30d
    ```

    Use proper Gantt chart syntax with:
    - title
    - dateFormat
    - sections for each phase
    - tasks with start dates and durations
    - Use format: task_name :start_date, duration
    - Or: task_name :after other_task, duration
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

        # Store raw diagram for validation
        return {
            "raw_diagram": markdown_diagram,
            "retry_count": 0
        }

    except Exception as e:
        logger.error(f"Error generating product roadmap: {e}")
        # Fallback response
        return {
            "response": {
                "type": "product-roadmap",
                "detail": f"Error generating product roadmap: {str(e)}"
            }
        }

def extract_mermaid_code(markdown_text: str) -> str:
    """Extract mermaid code from markdown fenced code block"""
    pattern = r'```mermaid\s*\n(.*?)```'
    match = re.search(pattern, markdown_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return markdown_text.strip()

def validate_diagram(state: ProductRoadmapState) -> ProductRoadmapState:
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

def finalize_response(state: ProductRoadmapState) -> ProductRoadmapState:
    """Create final response based on validation result"""
    validation_result = state.get("validation_result", {})
    raw_diagram = state.get("raw_diagram", "")

    if validation_result.get("valid", False):
        # Validation passed
        diagram_response = ProductRoadmapResponse(
            type="product-roadmap",
            detail=raw_diagram
        )
        output = ProductRoadmapOutput(type="diagram", response=diagram_response)
        return {"response": output.model_dump()["response"]}
    else:
        # Validation failed - still return the diagram but log the error
        errors = validation_result.get("errors", [])
        logger.warning(f"Product roadmap validation failed: {errors}")

        # Return diagram anyway with a warning in the metadata
        diagram_response = ProductRoadmapResponse(
            type="product-roadmap",
            detail=raw_diagram + f"\n\n<!-- Validation Warning: {errors} -->"
        )
        output = ProductRoadmapOutput(type="diagram", response=diagram_response)
        return {"response": output.model_dump()["response"]}

# Build LangGraph pipeline for Product Roadmap
workflow = StateGraph(ProductRoadmapState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate -> Validate -> Finalize
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_product_roadmap", generate_product_roadmap_diagram)
workflow.add_node("validate_diagram", validate_diagram)
workflow.add_node("finalize_response", finalize_response)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_product_roadmap")
workflow.add_edge("generate_product_roadmap", "validate_diagram")
workflow.add_edge("validate_diagram", "finalize_response")
workflow.add_edge("finalize_response", END)

# Compile graph
product_roadmap_graph = workflow.compile()
