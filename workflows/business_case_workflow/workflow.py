# workflows/business_case_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.business_case import BusinessCaseOutput, BusinessCaseResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from ..utils import extractor

class BusinessCaseState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_business_case(state: BusinessCaseState):
    """Generate Business Case document using OpenRouter AI"""
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

         # Using Gemini 2.5 Flash lite
        raw_output = model_client.gemini_completion(prompt)
        
        json_data = extractor.extract_json(raw_output)
        summary = "Activity Diagram"
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "Activity Diagram")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]

    except Exception as e:
        print(f"Error generating Business Case: {e}")

# Build LangGraph pipeline for Business Case
workflow = StateGraph(BusinessCaseState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_business_case", generate_business_case)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_business_case")
workflow.add_edge("generate_business_case", END)

# Compile graph
business_case_graph = workflow.compile()
