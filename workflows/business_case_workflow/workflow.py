# workflows/business_case_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional, List
from models import BusinessCaseState
from workflows.nodes import get_chat_history, get_context_node
from connect_model import get_model_client, set_request_model_config, reset_request_model_config, MODEL
from utils import extractor
from response import success_response, error_response

def generate_business_case(state: BusinessCaseState, config: Optional[dict] = None):
    """Generate Business Case document using OpenRouter AI"""
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
    Professional Business Analyst.

    ### TASK
    Create a complete Business Case for: {user_message}

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "title": "Business Case - [Project Name]",
    "content": "Markdown document with ALL sections below"
    }}

    ### REQUIRED STRUCTURE (Markdown)
    # Business Case Document
    ## Project: [Project Name]

    ### Executive Summary
    Overview, investment, benefits/ROI, recommendation

    ### Document Control
    Version, date, timeline

    ## 1. Business Problem
    - Problem statement
    - Impact analysis

    ## 2. Proposed Solution
    - Overview
    - Features (customer + business)
    - Technology approach

    ## 3. Cost Analysis
    - Initial investment (table)
    - Ongoing costs (table)

    ## 4. Benefits Analysis
    - Quantifiable benefits
    - Intangible benefits
    - 5-year summary (table)

    ## 5. Financial Analysis
    ROI, Payback Period, NPV, Break-even

    ## 6. Risk Assessment
    - Risks (table)
    - Mitigation budget

    ## 7. Strategic Alignment
    Strategy, competitive positioning, future opportunities

    ## 8. Implementation Approach
    - Timeline (table)
    - Success criteria

    ## 9. Alternatives Considered
    Options, pros/cons, rationale

    ## 10. Recommendation
    APPROVE / REJECT / DEFER + justification + next steps

    ## 11. Approval
    Approval table

    ## Appendices
    Supporting documents

    ### RULES
    - Return ONLY valid JSON (no markdown wrapper, no extra text)
    - Markdown must be well-structured
    - Include tables where specified
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
        summary = "Activity Diagram"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "Activity Diagram")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": success_response(summary, content)
        } # pyright: ignore[reportReturnType]

    except Exception as e:
        print(f"Error generating Business Case: {e}")
        return {
            "response": error_response("Business Case", f"Error generating Business Case: {e}")
        } # pyright: ignore[reportReturnType]
    finally:
        reset_request_model_config(token)

# Build LangGraph pipeline for Business Case
workflow = StateGraph(BusinessCaseState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_business_case", generate_business_case)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_business_case")
workflow.add_edge("generate_business_case", END)

# Compile graph
business_case_graph = workflow.compile()
