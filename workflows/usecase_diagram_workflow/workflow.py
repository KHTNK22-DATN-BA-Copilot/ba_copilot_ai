# workflows/usecase_diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.diagram import DiagramOutput, DiagramResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, process_ocr

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

class UsecaseDiagramState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    files: Optional[List]
    file_data: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_usecase_diagram_description(state: UsecaseDiagramState) -> UsecaseDiagramState:
    """Generate use-case diagram in markdown format using OpenRouter AI"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

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

# Build LangGraph pipeline for Use Case Diagram
workflow = StateGraph(UsecaseDiagramState)

# Add nodes in sequence: OCR -> Chat History -> Generate
workflow.add_node("process_ocr", process_ocr)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_usecase_diagram", generate_usecase_diagram_description)

# Set entry point and edges
workflow.set_entry_point("process_ocr")
workflow.add_edge("process_ocr", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_usecase_diagram")
workflow.add_edge("generate_usecase_diagram", END)

# Compile graph
usecase_diagram_graph = workflow.compile()
