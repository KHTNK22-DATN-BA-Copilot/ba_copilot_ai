# workflows/class_diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.diagram import DiagramOutput, DiagramResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL

class ClassDiagramState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_class_diagram_description(state: ClassDiagramState) -> ClassDiagramState:
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

    Create a detailed UML Class Diagram in Mermaid markdown format based on the requirement: {user_message}

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
            type="class_diagram",
            detail=markdown_diagram
        )
        output = DiagramOutput(type="diagram", response=diagram_response)

        return {"response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error generating class diagram: {e}")
        # Fallback response
        return {
            "response": {
                "type": "class_diagram",
                "detail": f"Error generating class diagram: {str(e)}"
            }
        }

# Build LangGraph pipeline for Class Diagram
workflow = StateGraph(ClassDiagramState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_class_diagram", generate_class_diagram_description)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_class_diagram")
workflow.add_edge("generate_class_diagram", END)

# Compile graph
class_diagram_graph = workflow.compile()
