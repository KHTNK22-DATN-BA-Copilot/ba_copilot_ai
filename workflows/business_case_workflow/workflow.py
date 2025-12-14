# workflows/business_case_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.business_case import BusinessCaseOutput, BusinessCaseResponse
from typing import TypedDict

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

class BusinessCaseState(TypedDict):
    user_message: str
    response: dict

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
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    prompt = f"""
    You are a professional Business Analyst. Create a comprehensive Business Case document for the following project:

    {state['user_message']}

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
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "BA-Copilot",
            },
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result_content = completion.choices[0].message.content
        business_case_data = extract_json(str(result_content))

        business_case_response = BusinessCaseResponse(
            title=business_case_data.get("title", "Business Case Document"),
            content=business_case_data.get("content", "")
        )

        output = BusinessCaseOutput(type="business-case", response=business_case_response)
        return {
            "user_message": state.get("user_message", ""),
            "response": output.model_dump()["response"]
        }

    except Exception as e:
        print(f"Error generating Business Case: {e}")
        # Fallback response
        return {
            "user_message": state.get("user_message", ""),
            "response": {
                "title": "Business Case Document",
                "content": f"Error generating business case: {str(e)}"
            }
        }

# Build LangGraph pipeline for Business Case
workflow = StateGraph(BusinessCaseState)

# Add node
workflow.add_node("generate_business_case", generate_business_case)

# Set entry point and finish
workflow.set_entry_point("generate_business_case")
workflow.add_edge("generate_business_case", END)

# Compile graph
business_case_graph = workflow.compile()
