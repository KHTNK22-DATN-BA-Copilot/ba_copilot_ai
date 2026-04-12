# workflows/class_diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from models.diagram import DiagramOutput, DiagramResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
import logging
from ..utils import extractor
# from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager

logger = logging.getLogger(__name__)

class ClassDiagramState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]
    raw_diagram: Optional[str]
    validation_result: Optional[dict]
    retry_count: int

def generate_class_diagram_description(state: ClassDiagramState):
    """Generate class diagram in markdown format using OpenRouter AI"""
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
    Expert UML Class Diagram designer (Mermaid).

    ### TASK
    Create a UML Class Diagram for: {user_message}

    ### REQUIREMENTS
    - Classes: attributes (+/-/#, name, type) and methods (params, return, visibility)
    - Relationships: association, aggregation, composition, inheritance, dependency
    - Include multiplicity where relevant
    - Use abstract classes/interfaces if needed
    - Apply design patterns if appropriate
    - Ensure clear, logical structure and valid Mermaid syntax

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Mermaid class diagram starting with 'classDiagram' (with backticks, use \\n for newlines)",
    "summary": "One-line concise description of the diagram"
    }}

    ### RULES
    - Do include ``` as markdown wrappers
    - Escape newlines properly (\\n)
    - No extra keys, no extra text
    - Must be valid JSON (parsable)
    """

    try:
        # Use OpenRouter (default)
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
        summary = "Class Diagram"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "Class Diagram")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]

    except Exception as e:
        print(f"Error generating class diagram: {e}")
     
# def extract_mermaid_code(markdown_text: str) -> str:
#     """Extract mermaid code from markdown fenced code block"""
#     pattern = r'```mermaid\s*\n(.*?)```'
#     match = re.search(pattern, markdown_text, re.DOTALL)
#     if match:
#         return match.group(1).strip()
#     return markdown_text.strip()

# def validate_diagram(state: ClassDiagramState) -> ClassDiagramState:
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

# def finalize_response(state: ClassDiagramState) -> ClassDiagramState:
#     """Create final response based on validation result"""
#     validation_result = state.get("validation_result", {})
#     raw_diagram = state.get("raw_diagram", "")
    
#     if validation_result.get("valid", False):
#         # Validation passed
#         diagram_response = DiagramResponse(
#             type="class_diagram",
#             detail=raw_diagram
#         )
#         output = DiagramOutput(type="diagram", response=diagram_response)
#         return {"response": output.model_dump()["response"]}
#     else:
#         # Validation failed - still return the diagram but log the error
#         errors = validation_result.get("errors", [])
#         logger.warning(f"Class diagram validation failed: {errors}")
        
#         # Return diagram anyway with a warning in the metadata
#         diagram_response = DiagramResponse(
#             type="class_diagram",
#             detail=raw_diagram + f"\n\n<!-- Validation Warning: {errors} -->"
#         )
#         output = DiagramOutput(type="diagram", response=diagram_response)
#         return {"response": output.model_dump()["response"]}

# Build LangGraph pipeline for Class Diagram
workflow = StateGraph(ClassDiagramState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_class_diagram", generate_class_diagram_description)
# workflow.add_node("validate_diagram", validate_diagram)
# workflow.add_node("finalize_response", finalize_response)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_class_diagram")
# workflow.add_edge("generate_class_diagram", "validate_diagram")
# workflow.add_edge("validate_diagram", "finalize_response")
# workflow.add_edge("finalize_response", END)
workflow.add_edge("generate_class_diagram", END)

# Compile graph
class_diagram_graph = workflow.compile()