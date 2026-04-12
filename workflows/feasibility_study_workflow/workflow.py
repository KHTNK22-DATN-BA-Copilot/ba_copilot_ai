# workflows/feasibility_study_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
# import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from models.feasibility_study import FeasibilityStudyOutput, FeasibilityStudyResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from ..utils import extractor

class FeasibilityStudyState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_feasibility_study(state: FeasibilityStudyState):
    """Generate Feasibility Study document using OpenRouter AI"""
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
    Professional Business Analyst (Feasibility Study).

    ### TASK
    Create a Feasibility Study for: {user_message}

    ### REQUIREMENTS
    Analyze:
    - Technical feasibility (technology, infrastructure)
    - Operational feasibility (resources, processes)
    - Economic feasibility (costs, benefits, ROI)
    - Schedule feasibility (timeline, constraints)
    - Legal feasibility (laws, compliance)

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Markdown feasibility study with sections below",
    "summary": "One-line feasibility conclusion (e.g., feasible / conditionally feasible / not feasible)"
    }}

    ### REQUIRED STRUCTURE (Markdown)
    # Feasibility Study
    ## Executive Summary
    ## Project Overview
    ## Technical Feasibility
    ## Operational Feasibility
    ## Economic Feasibility
    ## Schedule Feasibility
    ## Legal Feasibility
    ## Recommendations

    ### RULES
    - Return ONLY valid JSON (no markdown wrapper, no extra text)
    - Use clear, structured Markdown
    - Keep content concise but complete
    - Include key assumptions where relevant
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
        summary = "Feasibility Study"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "Feasibility Study")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating feasibility study: {e}")

# Build LangGraph pipeline for Feasibility Study
workflow = StateGraph(FeasibilityStudyState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_feasibility_study", generate_feasibility_study)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_feasibility_study")
workflow.add_edge("generate_feasibility_study", END)

# Compile graph
feasibility_study_graph = workflow.compile()
