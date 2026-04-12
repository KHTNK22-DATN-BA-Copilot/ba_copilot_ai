# workflows/high_level_requirements_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
# import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from ..utils import extractor

class HighLevelRequirementsState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_high_level_requirements(state: HighLevelRequirementsState):
    """Generate High-Level Requirements document using OpenRouter AI"""
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
    Professional Business Analyst (Requirements).

    ### TASK
    Create a High-Level Requirements document for: {user_message}

    ### REQUIREMENTS
    Include:
    - Functional requirements (categorized, unique IDs: FR-XXX)
    - Non-functional requirements (measurable, IDs: NFR-XXX)
    - Stakeholder needs
    - Constraints, assumptions, dependencies
    - Acceptance criteria (specific, measurable)

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Markdown requirements document with sections below",
    "summary": "One-line overview of the system scope and purpose"
    }}

    ### REQUIRED STRUCTURE (Markdown)
    # High-Level Requirements
    ## Introduction (Purpose, Scope, Objectives)
    ## Stakeholder Requirements
    ## Functional Requirements
    ## Non-Functional Requirements
    ## Constraints
    ## Assumptions
    ## Dependencies
    ## Acceptance Criteria
    ## Next Steps
    ## Approval

    ### RULES
    - Return ONLY valid JSON (no markdown wrapper, no extra text)
    - Use clear, structured Markdown
    - Use IDs for requirements (FR-XXX, NFR-XXX)
    - Include tables where appropriate
    - Keep content concise but complete
    - Ensure JSON is parsable (escape \\n properly)
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
        summary = "High-Level Requirements"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "High-Level Requirements")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating High-Level Requirements: {e}")

# Build LangGraph pipeline for High-Level Requirements
workflow = StateGraph(HighLevelRequirementsState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_high_level_requirements", generate_high_level_requirements)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_high_level_requirements")
workflow.add_edge("generate_high_level_requirements", END)

# Compile graph
high_level_requirements_graph = workflow.compile()
