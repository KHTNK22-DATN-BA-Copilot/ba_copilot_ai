# workflows/activity_diagram_workflow/workflow.py
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

class ActivityDiagramState(TypedDict):
    user_message: str
    response: dict
    document_id: Optional[str]
    files: Optional[List]
    file_data: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_activity_diagram_description(state: ActivityDiagramState) -> ActivityDiagramState:
    """Generate activity diagram in markdown format using OpenRouter AI"""
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

    Create a detailed UML Activity Diagram in Mermaid markdown format based on the requirement: {user_message}

    The diagram should include:
    - Start and end nodes (indicating the beginning and end of the workflow)
    - Activities (actions or processes that occur):
      * Use clear, action-oriented names (verb + object format, e.g., "Validate Input", "Process Payment")
      * Group related activities logically
    - Decision nodes (branching points in the flow):
      * Conditions that determine which path to take
      * Clear labels for each branch (e.g., "Valid" / "Invalid")
    - Merge nodes (where parallel or branching flows come together)
    - Swim lanes (if applicable) to show responsibilities across different actors or systems
    - Flow arrows showing the sequence and direction of activities
    - Parallel activities (fork/join) if tasks can happen concurrently
    - Guard conditions (constraints on transitions)

    IMPORTANT: Return ONLY the Mermaid markdown code block for the activity diagram, starting with triple backticks mermaid and ending with triple backticks.
    Do not include any explanatory text before or after the code block.

    Example format:
    Start with triple backticks mermaid
    graph TD with activities, decisions, and connections
    End with triple backticks
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
            type="activity_diagram",
            detail=markdown_diagram or ""
        )
        output = DiagramOutput(type="diagram", response=diagram_response)

        return {"response": output.model_dump()["response"]} # pyright: ignore[reportReturnType]

    except Exception as e:
        print(f"Error generating activity diagram: {e}")
        # Fallback response
        return {
            "response": {
                "type": "activity_diagram",
                "detail": f"Error generating activity diagram: {str(e)}"
            }
        } # pyright: ignore[reportReturnType]

# Build LangGraph pipeline for Activity Diagram
workflow = StateGraph(ActivityDiagramState)

# Add nodes in sequence: OCR -> Chat History -> Generate
workflow.add_node("process_ocr", process_ocr)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_activity_diagram", generate_activity_diagram_description)

# Set entry point and edges
workflow.set_entry_point("process_ocr")
workflow.add_edge("process_ocr", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_activity_diagram")
workflow.add_edge("generate_activity_diagram", END)

# Compile graph
activity_diagram_graph = workflow.compile()

