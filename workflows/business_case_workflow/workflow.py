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

class BusinessCaseState(TypedDict):
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

def generate_business_case(state: BusinessCaseState) -> BusinessCaseState:
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

    You are a professional Business Analyst. Create a comprehensive Business Case document for the following project:

    {user_message}

    Return the response in JSON format:
    {{
        "title": "Business Case - [Project Name]",
        "content": "Complete Business Case document in Markdown format with these sections:
                   # Business Case Document

                   ## Project: [Project Name]

                   ### Executive Summary
                   - Brief overview of the project proposal
                   - Investment required
                   - Expected benefits and ROI
                   - Recommendation

                   ### Document Control
                   - Version
                   - Date
                   - Project Timeline

                   ---

                   ## 1. Business Problem

                   ### 1.1 Problem Statement
                   - Clear description of the business problem
                   - Key issues and challenges

                   ### 1.2 Impact Analysis
                   - Current state challenges
                   - Business impact (revenue, costs, customer satisfaction)

                   ---

                   ## 2. Proposed Solution

                   ### 2.1 Solution Overview
                   - Description of the proposed solution
                   - Key components

                   ### 2.2 Solution Features
                   - Customer-facing features
                   - Business features

                   ### 2.3 Technology Approach
                   - Technology stack
                   - Architecture approach

                   ---

                   ## 3. Cost Analysis

                   ### 3.1 Initial Investment
                   | Category | Description | Cost |
                   |----------|-------------|------|

                   ### 3.2 Ongoing Costs (Annual)
                   | Category | Description | Annual Cost |
                   |----------|-------------|-------------|

                   ---

                   ## 4. Benefits Analysis

                   ### 4.1 Quantifiable Benefits
                   - Revenue increase projections
                   - Operational efficiency gains
                   - Error reduction
                   - Cost savings

                   ### 4.2 Intangible Benefits
                   - Customer satisfaction improvements
                   - Brand enhancement
                   - Market expansion opportunities
                   - Strategic advantages

                   ### 4.3 Total Benefits Summary (5-Year)
                   | Year | Revenue Increase | Cost Savings | Total Benefits |
                   |------|------------------|--------------|----------------|

                   ---

                   ## 5. Financial Analysis

                   ### 5.1 Return on Investment (ROI)
                   - ROI calculation and percentage

                   ### 5.2 Payback Period
                   - Time to recover initial investment

                   ### 5.3 Net Present Value (NPV)
                   - NPV calculation with discount rate

                   ### 5.4 Break-Even Analysis
                   - Break-even point calculation

                   ---

                   ## 6. Risk Assessment

                   ### 6.1 Identified Risks
                   | Risk | Probability | Impact | Mitigation Strategy |
                   |------|-------------|--------|---------------------|

                   ### 6.2 Risk Mitigation Budget
                   - Contingency reserve allocation

                   ---

                   ## 7. Strategic Alignment

                   ### 7.1 Organizational Strategy
                   - How project aligns with strategic initiatives

                   ### 7.2 Competitive Positioning
                   - Market requirements and competitive advantages

                   ### 7.3 Future Opportunities
                   - Platform for future initiatives

                   ---

                   ## 8. Implementation Approach

                   ### 8.1 Project Timeline
                   | Phase | Duration | Key Activities |
                   |-------|----------|----------------|

                   ### 8.2 Success Criteria
                   - Measurable success criteria

                   ---

                   ## 9. Alternatives Considered

                   ### 9.1 Alternative Options
                   - Pros and cons of each alternative
                   - Decision rationale

                   ---

                   ## 10. Recommendation
                   - Clear recommendation (APPROVE/REJECT/DEFER)
                   - Justification
                   - Next steps

                   ---

                   ## 11. Approval
                   | Role | Name | Recommendation | Signature | Date |
                   |------|------|----------------|-----------|------|

                   ---

                   ## Appendices
                   - List of supporting documents and references"
    }}

    Return only JSON, no additional text.
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
        business_case_data = extract_json(str(result_content))

        business_case_response = BusinessCaseResponse(
            title=business_case_data.get("title", "Business Case Document"),
            content=business_case_data.get("content", "")
        )

        output = BusinessCaseOutput(type="business-case", response=business_case_response)
        return {"response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error generating Business Case: {e}")
        # Fallback response
        return {
            "response": {
                "title": "Business Case Document",
                "content": f"Error generating business case: {str(e)}"
            }
        }

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
