# workflows/stakeholder_register_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL

class StakeholderRegisterState(TypedDict):
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

def generate_stakeholder_register(state: StakeholderRegisterState) -> StakeholderRegisterState:
    """Generate Stakeholder Register document using OpenRouter AI"""
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
    You are a professional Business Analyst. With strong expertise in stakeholder management, communication planning, and project governance.
    
    ### CONTEXT
    Create a comprehensive Stakeholder Register document for the following project:

    Project Requirements: {user_message}

    ### INSTRUCTIONS
    1. Read and analyze the context in {context_str} and **<CONTEXT** section above.
    2. Create a detailed Stakeholder Register covering all specified sections.
    3. Ensure clarity, completeness, and correctness in the document.
    
    ### NOTE
    1. Use Markdown format for the Stakeholder Register document.
    2. Follow best practices for structuring Stakeholder Registers.
    
    ### EXAMPLE OUTPUT
    Return the response in JSON format with this structure:
    {{
        "title": "Stakeholder Register - [Project Name]",
        "content": "Complete markdown document with sections:
            1. Document Information (Date, Version, Prepared by)
            2. Executive Summary
            3. Stakeholder List (Internal and External with details)
            4. Stakeholder Analysis Matrix
            5. Communication Plan
            6. Engagement Activities
            7. Risk Assessment
            8. Conclusion"
    }}

    For each stakeholder include:
    - Name and Role
    - Department/Organization
    - Interest Level (High/Medium/Low)
    - Influence Level (High/Medium/Low)
    - Engagement Strategy
    - Communication Preferences
    - Key Concerns

    Include a stakeholder analysis matrix table showing Power, Interest, and Management Strategy.
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
            "title": doc_data.get("title", "Stakeholder Register"),
            "content": doc_data.get("content", "")
        }

        return {"response": response_data}

    except Exception as e:
        print(f"Error generating Stakeholder Register: {e}")
        # Fallback response
        return {
            "response": {
                "title": "Stakeholder Register",
                "content": f"Error generating document: {str(e)}"
            }
        }

# Build LangGraph pipeline for Stakeholder Register
workflow = StateGraph(StakeholderRegisterState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_stakeholder_register", generate_stakeholder_register)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_stakeholder_register")
workflow.add_edge("generate_stakeholder_register", END)

# Compile graph
stakeholder_register_graph = workflow.compile()
