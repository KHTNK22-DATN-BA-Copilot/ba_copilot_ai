# workflows/feasibility_study_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
# import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional, List
from models import FeasibilityStudyState
from workflows.nodes import get_chat_history, get_context_node
from connect_model import get_model_client, set_request_model_config, reset_request_model_config, MODEL
from utils import extractor
from response import success_response, error_response

def generate_feasibility_study(state: FeasibilityStudyState, config: Optional[dict] = None):
    """Generate Feasibility Study document using OpenRouter AI"""
    model_client = get_model_client()
    cfg = (config or {}).get("configurable", {})
    token = set_request_model_config(
        provider=cfg.get("provider"),
        model_name=cfg.get("model_name"),
        api_key=cfg.get("api_key"),
    )

    # Build system prompt
    user_message = state['user_message']
    extracted_text = state.get('extracted_text', '')
    chat_context = state.get('chat_context') or []
    prompt = f"""
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

    messages: List[dict] = [
        {"role": "system", "content": prompt},
        *chat_context,
    ]
    if extracted_text:
        messages.append({"role": "assistant", "content": extracted_text})
    messages.append({"role": "user", "content": user_message})

    try:
        response = model_client.chat_completion(
            messages=messages,
            model=cfg.get("model_name") or MODEL,
        )
        raw_output = response.choices[0].message.content or ""

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
            "response": success_response(summary, content)
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating feasibility study: {e}")
        return {
            "response": error_response("Feasibility Study", f"Error generating feasibility study: {e}")
        } # pyright: ignore[reportReturnType]
    finally:
        reset_request_model_config(token)

# Build LangGraph pipeline for Feasibility Study
workflow = StateGraph(FeasibilityStudyState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_feasibility_study", generate_feasibility_study)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_feasibility_study")
workflow.add_edge("generate_feasibility_study", END)

# Compile graph
feasibility_study_graph = workflow.compile()
