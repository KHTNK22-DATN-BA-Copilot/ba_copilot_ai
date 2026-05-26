# workflows/hld_tech_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional, List
from models import HLDTechState
from workflows.nodes import get_chat_history, get_context_node
from connect_model import get_model_client, set_request_model_config, reset_request_model_config, MODEL
from utils import extractor
from response import success_response, error_response

def generate_hld_tech(state: HLDTechState, config: Optional[dict] = None):
    """Generate Tech Stack Selection document using OpenRouter AI"""
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
    Senior Technical Architect (tech stack selection for scalable, maintainable systems).

    ### TASK
    Design a Technology Stack Selection for: {user_message}

    ### REQUIREMENTS
    The "content" MUST be a Markdown document (use \\n) with EXACT structure:

    # Technology Stack Selection - <Project Name>

    ## 1. Executive Summary
    - 1–2 sentence overview

    ## 2. Frontend Technologies
    - Framework, state management, UI, tools

    ## 3. Backend Technologies
    - Language, framework, API design, auth

    ## 4. Database and Data Layer
    - Primary DB, caching, search, analytics

    ## 5. Infrastructure and DevOps
    - CI/CD, containerization, monitoring, logging

    ## 6. Technology Justification
    - Why each key tech is chosen (performance, scalability, cost, team fit)

    ## 7. Alternatives Considered
    - Key alternatives + brief rejection reasons

    - Use concise bullet points
    - Use concrete technologies (e.g., React, Node.js, PostgreSQL, Docker)

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Markdown document following REQUIRED structure (use \\n for newlines)",
    "summary": "One-line tech stack summary"
    }}

    ### RULES
    - Output JSON ONLY (no markdown wrappers, no explanations)
    - No extra keys, no missing keys
    - Do NOT change section titles or order
    - Escape \\n properly
    - Be concise but complete
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
        summary = "HLD Tech"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "HLD Tech")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": success_response(summary, content)
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating tech stack selection: {e}")
        return {
            "response": error_response("HLD Tech", f"Error generating tech stack selection: {e}")
        } # pyright: ignore[reportReturnType]
    finally:
        reset_request_model_config(token)

# Build LangGraph pipeline for Tech Stack Selection
workflow = StateGraph(HLDTechState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_hld_tech", generate_hld_tech)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_hld_tech")
workflow.add_edge("generate_hld_tech", END)

# Compile graph
hld_tech_graph = workflow.compile()
