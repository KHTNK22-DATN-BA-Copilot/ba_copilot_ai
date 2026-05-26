# workflows/cost_benefit_analysis_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
# import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional, List
from models import CostBenefitAnalysisState
from workflows.nodes import get_chat_history, get_context_node
from connect_model import get_model_client, set_request_model_config, reset_request_model_config, MODEL
from utils import extractor
from response import success_response, error_response

def generate_cost_benefit_analysis(state: CostBenefitAnalysisState, config: Optional[dict] = None):
    """Generate Cost-Benefit Analysis document using OpenRouter AI"""
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
    Professional Business Analyst (Cost-Benefit Analysis).

    ### TASK
    Create a Cost-Benefit Analysis for: {user_message}

    ### REQUIREMENTS
    Analyze:
    - Cost breakdown (development, operational, maintenance)
    - Benefits (tangible and intangible, quantified if possible)
    - ROI (with formula and projection)
    - NPV (with discount rate assumption)
    - Payback period (break-even point)
    - Key financial assumptions

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "summary": "One-line financial conclusion (e.g., high ROI, viable investment, not financially justified)",
    "content": "Markdown cost-benefit analysis with sections below"
    }}

    ### REQUIRED STRUCTURE (Markdown)
    # Cost-Benefit Analysis
    ## Executive Summary
    ## Project Overview
    ## Cost Analysis
    ## Benefit Analysis
    ## ROI Calculation
    ## NPV Analysis
    ## Payback Period
    ## Assumptions
    ## Sensitivity Analysis
    ## Recommendations

    ### RULES
    - Return ONLY valid JSON (no markdown wrapper, no extra text)
    - ALL values must be strings
    - Escape \\n properly
    - Do NOT return empty fields
    - Use realistic numbers or reasonable estimates
    - If data is missing, make assumptions and state them
    - Keep content concise but complete
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
        summary = "Cost Benefit Analysis"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "Cost Benefit Analysis")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": success_response(summary, content)
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating cost-benefit analysis: {e}")
        return {
            "response": error_response(
                "Cost Benefit Analysis",
                f"Error generating cost-benefit analysis: {e}",
            )
        } # pyright: ignore[reportReturnType]
    finally:
        reset_request_model_config(token)

# Build LangGraph pipeline for Cost-Benefit Analysis
workflow = StateGraph(CostBenefitAnalysisState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_cost_benefit_analysis", generate_cost_benefit_analysis)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_cost_benefit_analysis")
workflow.add_edge("generate_cost_benefit_analysis", END)

# Compile graph
cost_benefit_analysis_graph = workflow.compile()
