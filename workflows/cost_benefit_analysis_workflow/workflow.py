# workflows/cost_benefit_analysis_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.cost_benefit_analysis import CostBenefitAnalysisOutput, CostBenefitAnalysisResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL

class CostBenefitAnalysisState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def extract_json(text: str) -> dict:
    """Extract JSON from text response"""
    try:
        # Find JSON block
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        return {}
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return {}

def generate_cost_benefit_analysis(state: CostBenefitAnalysisState) -> CostBenefitAnalysisState:
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
    You are a professional Business Analyst. With strong expertise in financial analysis, project evaluation, and cost-benefit assessment.
    
    ### CONTEXT
    Create a detailed Cost-Benefit Analysis document for the following requirement: {user_message}

    Provide comprehensive financial analysis including:
    1. Cost Analysis - All project costs (development, implementation, operational, maintenance)
    2. Benefit Analysis - All expected benefits (tangible and intangible)
    3. ROI Calculation - Return on Investment with formulas and projections
    4. NPV Analysis - Net Present Value calculation with discount rates
    5. Payback Period - Time required to recover the investment

    ### INSTRUCTIONS
    1. Read and analyze the context in {context_str} and **<CONTEXT** section above.
    2. Create a comprehensive Cost-Benefit Analysis document covering all specified sections.
    3. Ensure clarity, completeness, and correctness in the document.
    
    ### NOTE
    1. Use Markdown format for the Cost-Benefit Analysis document.
    2. Follow best practices for structuring financial analysis documentation.
    
    ### EXAMPLE OUTPUT
    Return the response in JSON format:
    {{
        "title": "Cost-Benefit Analysis - [Project Name]",
        "executive_summary": "Brief overview of financial analysis and recommendations",
        "cost_analysis": "Detailed breakdown of all costs (initial, ongoing, hidden costs)",
        "benefit_analysis": "Comprehensive analysis of all benefits with quantification where possible",
        "roi_calculation": "ROI calculation with methodology and multi-year projections",
        "npv_analysis": "Net Present Value calculation with discount rate assumptions",
        "payback_period": "Payback period calculation and break-even analysis",
        "detail": "Complete detailed cost-benefit analysis in Markdown format with sections:
                   1. Executive Summary
                   2. Project Overview
                   3. Cost Analysis (detailed breakdown)
                   4. Benefit Analysis (quantified where possible)
                   5. ROI Calculation and Projections
                   6. NPV Analysis
                   7. Payback Period and Break-Even Analysis
                   8. Sensitivity Analysis
                   9. Recommendations and Conclusion"
    }}
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

        result_content = completion.choices[0].message.content
        analysis_data = extract_json(result_content)

        analysis_response = CostBenefitAnalysisResponse(
            title=analysis_data.get("title", "Cost-Benefit Analysis"),
            executive_summary=analysis_data.get("executive_summary", ""),
            cost_analysis=analysis_data.get("cost_analysis", ""),
            benefit_analysis=analysis_data.get("benefit_analysis", ""),
            roi_calculation=analysis_data.get("roi_calculation", ""),
            npv_analysis=analysis_data.get("npv_analysis", ""),
            payback_period=analysis_data.get("payback_period", ""),
            detail=analysis_data.get("detail", "")
        )

        output = CostBenefitAnalysisOutput(type="cost-benefit-analysis", response=analysis_response)
        return {"response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error generating cost-benefit analysis: {e}")
        # Fallback response
        return {
            "response": {
                "title": "Cost-Benefit Analysis",
                "executive_summary": "Error generating cost-benefit analysis",
                "cost_analysis": "Error",
                "benefit_analysis": "Error",
                "roi_calculation": "Error",
                "npv_analysis": "Error",
                "payback_period": "Error",
                "detail": f"Error: {str(e)}"
            }
        }

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
