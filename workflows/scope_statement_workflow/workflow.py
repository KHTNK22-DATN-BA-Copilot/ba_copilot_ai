# workflows/scope_statement_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.scope_statement import ScopeStatementOutput, ScopeStatementResponse
from typing import TypedDict

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

class ScopeStatementState(TypedDict):
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

def generate_scope_statement(state: ScopeStatementState) -> ScopeStatementState:
    """Generate Scope Statement document using OpenRouter AI"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    prompt = f"""
    You are a professional Business Analyst. Create a detailed Project Scope Statement document for the following project:

    {state['user_message']}

    Return the response in JSON format:
    {{
        "title": "Project Scope Statement - [Project Name]",
        "content": "Complete Project Scope Statement document in Markdown format with these sections:
                   # Project Scope Statement
                   
                   ## Project: [Project Name]
                   
                   ### Document Control
                   - Version
                   - Date
                   - Approved By
                   - Last Updated
                   
                   ---
                   
                   ## 1. Project Overview
                   
                   ### 1.1 Project Purpose
                   - Business need or opportunity
                   - Project objectives
                   
                   ### 1.2 Project Description
                   - High-level description of the project
                   - Expected outcomes
                   
                   ### 1.3 Project Justification
                   - Why this project is necessary
                   - Strategic alignment
                   
                   ---
                   
                   ## 2. Project Scope
                   
                   ### 2.1 In Scope
                   - Detailed list of what IS included in the project
                   - Features and functionalities to be delivered
                   - Work to be performed
                   - Deliverables to be produced
                   
                   ### 2.2 Out of Scope
                   - Detailed list of what IS NOT included
                   - Features explicitly excluded
                   - Boundaries of the project
                   
                   ---
                   
                   ## 3. Deliverables
                   
                   ### 3.1 Major Deliverables
                   | Deliverable | Description | Acceptance Criteria |
                   |-------------|-------------|---------------------|
                   
                   ### 3.2 Milestones
                   | Milestone | Target Date | Description |
                   |-----------|-------------|-------------|
                   
                   ---
                   
                   ## 4. Requirements Summary
                   
                   ### 4.1 Functional Requirements
                   - High-level functional requirements
                   
                   ### 4.2 Non-Functional Requirements
                   - Performance requirements
                   - Security requirements
                   - Scalability requirements
                   - Compliance requirements
                   
                   ### 4.3 Technical Requirements
                   - Technology constraints
                   - Integration requirements
                   
                   ---
                   
                   ## 5. Constraints
                   
                   ### 5.1 Project Constraints
                   - Time constraints
                   - Budget constraints
                   - Resource constraints
                   - Technology constraints
                   - Regulatory/compliance constraints
                   
                   ---
                   
                   ## 6. Assumptions
                   
                   ### 6.1 Project Assumptions
                   - List of assumptions made during planning
                   - Resource availability assumptions
                   - Technology assumptions
                   - Stakeholder availability assumptions
                   
                   ---
                   
                   ## 7. Dependencies
                   
                   ### 7.1 Internal Dependencies
                   - Dependencies on other projects/initiatives
                   - Dependencies on internal resources
                   
                   ### 7.2 External Dependencies
                   - Third-party vendor dependencies
                   - External system dependencies
                   
                   ---
                   
                   ## 8. Success Criteria
                   
                   ### 8.1 Project Success Criteria
                   - Measurable criteria for project success
                   - Quality standards
                   - Performance benchmarks
                   
                   ### 8.2 Acceptance Criteria
                   - Criteria for deliverable acceptance
                   - Sign-off requirements
                   
                   ---
                   
                   ## 9. Stakeholders
                   
                   ### 9.1 Key Stakeholders
                   | Stakeholder | Role | Responsibility |
                   |-------------|------|----------------|
                   
                   ---
                   
                   ## 10. Change Management
                   
                   ### 10.1 Scope Change Process
                   - How scope changes will be handled
                   - Change request procedures
                   - Approval authority
                   
                   ---
                   
                   ## 11. Risks and Issues
                   
                   ### 11.1 Known Risks
                   - Initial risk identification
                   - High-level mitigation strategies
                   
                   ### 11.2 Known Issues
                   - Current issues affecting scope
                   
                   ---
                   
                   ## 12. Approval
                   
                   | Role | Name | Signature | Date |
                   |------|------|-----------|------|
                   | **Project Sponsor** | | | |
                   | **Project Manager** | | | |
                   | **Business Analyst** | | | |
                   | **Key Stakeholder** | | | |"
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
        scope_statement_data = extract_json(str(result_content))

        scope_statement_response = ScopeStatementResponse(
            title=scope_statement_data.get("title", "Project Scope Statement"),
            content=scope_statement_data.get("content", "")
        )

        output = ScopeStatementOutput(type="scope-statement", response=scope_statement_response)
        return {
            "user_message": state.get("user_message", ""),
            "response": output.model_dump()["response"]
        }

    except Exception as e:
        print(f"Error generating Scope Statement: {e}")
        # Fallback response
        return {
            "user_message": state.get("user_message", ""),
            "response": {
                "title": "Project Scope Statement",
                "content": f"Error generating scope statement: {str(e)}"
            }
        }

# Build LangGraph pipeline for Scope Statement
workflow = StateGraph(ScopeStatementState)

# Add node
workflow.add_node("generate_scope_statement", generate_scope_statement)

# Set entry point and finish
workflow.set_entry_point("generate_scope_statement")
workflow.add_edge("generate_scope_statement", END)

# Compile graph
scope_statement_graph = workflow.compile()
