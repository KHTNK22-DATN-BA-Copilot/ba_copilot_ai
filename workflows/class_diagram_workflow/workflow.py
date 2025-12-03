# workflows/class_diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
import sys
import os
import re
import logging
import re
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.diagram import DiagramOutput, DiagramResponse
from typing import TypedDict, Optional
from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager
from typing import TypedDict, Optional
from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

class ClassDiagramState(TypedDict):
    user_message: str
    response: dict
    raw_diagram: Optional[str]
    validation_result: Optional[dict]
    retry_count: int
    raw_diagram: Optional[str]
    validation_result: Optional[dict]
    retry_count: int

def generate_class_diagram_description(state: ClassDiagramState) -> ClassDiagramState:
    """Generate class diagram in markdown format using OpenRouter AI"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    prompt = f"""
    Create a detailed UML Class Diagram in Mermaid markdown format based on the requirement: {state['user_message']}

    The diagram should include:
    - Classes with their attributes (name, type, visibility: +public, -private, #protected)
    - Methods/Operations for each class (name, parameters, return type, visibility)
    - Relationships between classes:
      * Association (simple connection between classes)
      * Aggregation (has-a relationship, hollow diamond)
      * Composition (strong ownership, filled diamond)
      * Inheritance (is-a relationship, hollow arrow)
      * Dependency (uses, dashed arrow)
      * Multiplicity (1, 0..1, 1..*, 0..*, etc.)
    - Abstract classes and interfaces if applicable
    - Key design patterns if relevant

    IMPORTANT: Return ONLY the Mermaid markdown code block for the class diagram, starting with ```mermaid and ending with ```.
    Do not include any explanatory text before or after the code block.

    Example format:
    ```mermaid
    classDiagram
        class ClassName {{
            +String attribute
            -int privateAttribute
            +method()
        }}
        ClassA --|> ClassB : Inheritance
        ClassC --* ClassD : Composition
    ```
    """

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "BA-Copilot",
            },
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        markdown_diagram = completion.choices[0].message.content

        # Store raw diagram for validation
        # type: ignore[return-value] - Partial state update is valid for LangGraph
        return {
            "raw_diagram": markdown_diagram,
            "retry_count": 0
        }

    except Exception as e:
        print(f"Error generating class diagram: {e}")
        # Fallback response
        # type: ignore[return-value] - Partial state update is valid for LangGraph
        return {
            "response": {
                "type": "class_diagram",
                "detail": f"Error generating class diagram: {str(e)}"
            }
        }

def extract_mermaid_code(markdown_text: str) -> str:
    """Extract mermaid code from markdown fenced code block"""
    pattern = r'```mermaid\s*\n(.*?)```'
    match = re.search(pattern, markdown_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return markdown_text.strip()

def validate_diagram(state: ClassDiagramState) -> ClassDiagramState:
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

def finalize_response(state: ClassDiagramState) -> ClassDiagramState:
    """Create final response based on validation result"""
    validation_result = state.get("validation_result", {})
    raw_diagram = state.get("raw_diagram", "")
    
    if validation_result.get("valid", False):
        # Validation passed
        diagram_response = DiagramResponse(
            type="class_diagram",
            detail=raw_diagram
        )
        output = DiagramOutput(type="diagram", response=diagram_response)
        return {"response": output.model_dump()["response"]}
    else:
        # Validation failed - still return the diagram but log the error
        errors = validation_result.get("errors", [])
        logger.warning(f"Class diagram validation failed: {errors}")
        
        # Return diagram anyway with a warning in the metadata
        diagram_response = DiagramResponse(
            type="class_diagram",
            detail=raw_diagram + f"\n\n<!-- Validation Warning: {errors} -->"
        )
        output = DiagramOutput(type="diagram", response=diagram_response)
        return {"response": output.model_dump()["response"]}

# Build LangGraph pipeline for Class Diagram
workflow = StateGraph(ClassDiagramState)

# Add nodes
workflow.add_node("generate_class_diagram", generate_class_diagram_description)
workflow.add_node("validate_diagram", validate_diagram)
workflow.add_node("finalize_response", finalize_response)

# Set entry point and edges
workflow.set_entry_point("generate_class_diagram")
workflow.add_edge("generate_class_diagram", "validate_diagram")
workflow.add_edge("validate_diagram", "finalize_response")
workflow.add_edge("finalize_response", END)

# Compile graph
class_diagram_graph = workflow.compile()
