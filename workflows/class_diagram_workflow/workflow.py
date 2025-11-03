# workflows/class_diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.diagram import DiagramOutput, DiagramResponse
from typing import TypedDict

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

class ClassDiagramState(TypedDict):
    user_message: str
    response: dict

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

# Add node
workflow.add_node("generate_class_diagram", generate_class_diagram_description)

# Set entry point and finish
workflow.set_entry_point("generate_class_diagram")
workflow.add_edge("generate_class_diagram", END)

# Compile graph
class_diagram_graph = workflow.compile()
