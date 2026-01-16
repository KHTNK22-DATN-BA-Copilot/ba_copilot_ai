# workflows/requirements_management_plan_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL

class RequirementsManagementPlanState(TypedDict):
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

def generate_requirements_management_plan(state: RequirementsManagementPlanState) -> RequirementsManagementPlanState:
    """Generate Requirements Management Plan document using OpenRouter AI"""
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
    You are a professional Business Analyst. With strong expertise in creating detailed and structured Requirements Management Plans that effectively outline the processes for managing project requirements throughout the project lifecycle.
    
    ### CONTEXT
    Create a comprehensive Requirements Management Plan for the following project:
    Project Requirements: {user_message}

    ### INSTRUCTIONS
    1. Read and analyze the context in {context_str} and **<CONTEXT** section above.
    2. Create a detailed Requirements Management Plan covering all specified sections.
    3. Ensure clarity, completeness, and correctness in the document.
    
    ### NOTE
    1. Use markdown format for the document.
    2. Follow best practices for structuring Requirements Management Plans.
    
    ### EXAMPLE OUTPUT
    Return the response in JSON format with this structure:
    {{
        "title": "Requirements Management Plan - [Project Name]",
        "content": "Complete markdown document with sections:
            1. Introduction (Purpose, Scope, Objectives)
            2. Requirements Management Approach (Methodology Alignment, Requirements Levels)
            3. Requirements Elicitation (Techniques, Schedule with table)
            4. Requirements Analysis (Techniques, Prioritization using MoSCoW)
            5. Requirements Documentation (Standards, Tools, Attributes)
            6. Requirements Validation (Techniques, Acceptance Criteria Checklist)
            7. Requirements Traceability (Matrix, Tools)
            8. Requirements Change Management (Process, Change Control Board, Criteria)
            9. Communication Plan (Table with Audience, Method, Frequency, Content)
            10. Roles and Responsibilities (Product Owner, BA, Scrum Master, Dev Team, Stakeholders)
            11. Tools and Techniques
            12. Metrics and Reporting
            13. Quality Assurance
            14. Training and Support
            15. Appendices
            16. Document Approval section with signature table"
    }}

    Include:
    - User Story Format template
    - MoSCoW prioritization method
    - Change request process flowchart (in text format)
    - Requirements attributes list
    - Traceability matrix example table
    - Communication plan table
    - Metrics for tracking requirements (velocity, volatility, defect density)
    - Quality criteria checklist
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
        doc_data = extract_json(str(result_content))

        response_data = {
            "title": doc_data.get("title", "Requirements Management Plan"),
            "content": doc_data.get("content", "")
        }

        return {"response": response_data}

    except Exception as e:
        print(f"Error generating Requirements Management Plan: {e}")
        # Fallback response
        return {
            "response": {
                "title": "Requirements Management Plan",
                "content": f"Error generating document: {str(e)}"
            }
        }

# Build LangGraph pipeline for Requirements Management Plan
workflow = StateGraph(RequirementsManagementPlanState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_requirements_management_plan", generate_requirements_management_plan)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_requirements_management_plan")
workflow.add_edge("generate_requirements_management_plan", END)

# Compile graph
requirements_management_plan_graph = workflow.compile()
