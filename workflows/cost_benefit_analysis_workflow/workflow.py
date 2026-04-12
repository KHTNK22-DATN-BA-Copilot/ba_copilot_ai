# workflows/cost_benefit_analysis_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
# import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from models.cost_benefit_analysis import CostBenefitAnalysisOutput, CostBenefitAnalysisResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from ..utils import extractor
class CostBenefitAnalysisState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_cost_benefit_analysis(state: CostBenefitAnalysisState):
    """Generate Cost-Benefit Analysis document using OpenRouter AI"""
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
        summary = "Cost Benefit Analysis"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "Cost Benefit Analysis")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating cost-benefit analysis: {e}")

# Build LangGraph pipeline for Cost-Benefit Analysis
workflow = StateGraph(CostBenefitAnalysisState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_cost_benefit_analysis", generate_cost_benefit_analysis)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_cost_benefit_analysis")
workflow.add_edge("generate_cost_benefit_analysis", END)

# Compile graph
cost_benefit_analysis_graph = workflow.compile()
