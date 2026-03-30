# workflows/product_roadmap_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from models.product_roadmap import ProductRoadmapOutput, ProductRoadmapResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
# from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager
from ..utils import extractor

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

def generate_product_roadmap_diagram(state: ProductRoadmapState):
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

    ### ROLE
    Product Manager (roadmap planning, Mermaid Gantt).

    ### TASK
    Create a Product Roadmap for: {user_message}

    ### REQUIREMENTS
    - Use Mermaid Gantt
    - Include:
    - title
    - dateFormat YYYY-MM-DD
    - sections: Planning, Design, Development, Testing, Deployment
    - tasks with:
        - start date + duration (e.g., 2024-01-01, 30d) OR
        - dependencies using "after"
    - Timeline must span multiple months
    - Use clear, realistic task names and sequencing

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Mermaid Gantt chart starting with 'gantt' (no backticks, use \\n for newlines)",
    "summary": "One-line roadmap summary"
    }}

    ### RULES
    - Do NOT include ``` or markdown wrappers
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
        summary = "Product Roadmap"
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "Product Roadmap")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        logger.exception(f"Error generating product roadmap: {e}")

# def validate_diagram(state: ProductRoadmapState) -> ProductRoadmapState:
#     """Validate the generated mermaid diagram"""
#     raw_diagram = state.get("raw_diagram", "")
#     if not raw_diagram:
#         logger.error("No diagram to validate")
#         return {
#             "validation_result": {"valid": False, "errors": ["No diagram generated"]}
#         }

#     # Extract mermaid code from markdown
#     mermaid_code = extract_mermaid_code(raw_diagram)
#     # Clean up mermaid_code: remove lines that are not valid Mermaid syntax
#     lines = mermaid_code.splitlines()
#     cleaned_lines = []
#     for line in lines:
#         if re.match(r'^(Architecture Design|System Architec)', line.strip()):
#             continue
#         cleaned_lines.append(line)
#     cleaned_mermaid = '\n'.join(cleaned_lines).strip()
#     validator = MermaidSubprocessManager()
#     try:
#         result = validator.validate_sync(cleaned_mermaid)
#         logger.info(f"Validation result: {result.get('valid', False)}")
#         return {"validation_result": result}
#     except Exception as e:
#         logger.error(f"Validation failed: {e}")
#         return {
#             "validation_result": {"valid": False, "errors": [str(e)]}
#         }
#     finally:
#         validator.sync_client.close()

# def finalize_response(state: ProductRoadmapState) -> ProductRoadmapState:
#     """Create final response based on validation result"""
#     validation_result = state.get("validation_result", {})
#     raw_diagram = state.get("raw_diagram", "")

#     if validation_result.get("valid", False):
#         # Validation passed
#         diagram_response = ProductRoadmapResponse(
#             type="product-roadmap",
#             detail=raw_diagram
#         )
#         output = ProductRoadmapOutput(type="diagram", response=diagram_response)
#         return {"response": output.model_dump()["response"]}
#     else:
#         # Validation failed - still return the diagram but log the error
#         errors = validation_result.get("errors", [])
#         logger.warning(f"Product roadmap validation failed: {errors}")

#         # Return diagram anyway with a warning in the metadata
#         diagram_response = ProductRoadmapResponse(
#             type="product-roadmap",
#             detail=raw_diagram + f"\n\n<!-- Validation Warning: {errors} -->"
#         )
#         output = ProductRoadmapOutput(type="diagram", response=diagram_response)
#         return {"response": output.model_dump()["response"]}

# Build LangGraph pipeline for Product Roadmap
workflow = StateGraph(ProductRoadmapState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate -> Validate -> Finalize
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_product_roadmap", generate_product_roadmap_diagram)
# workflow.add_node("validate_diagram", validate_diagram)
# workflow.add_node("finalize_response", finalize_response)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_product_roadmap")
# workflow.add_edge("generate_product_roadmap", "validate_diagram")
# workflow.add_edge("validate_diagram", "finalize_response")
# workflow.add_edge("finalize_response", END)
workflow.add_edge("generate_product_roadmap", END)

# Compile graph
product_roadmap_graph = workflow.compile()
