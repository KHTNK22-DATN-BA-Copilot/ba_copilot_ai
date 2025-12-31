# workflows/risk_register_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.risk_register import RiskRegisterOutput, RiskRegisterResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL

class RiskRegisterState(TypedDict):
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

def generate_risk_register(state: RiskRegisterState) -> RiskRegisterState:
    """Generate Risk Register document using OpenRouter AI"""
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
    You are a professional Business Analyst. With strong expertise in risk management, project risk assessment, and mitigation planning.
    
    ### CONTEXT
    Create a comprehensive Risk Register document for the following requirement: {user_message}

    Identify and analyze all potential project risks including:
    1. Risk Identification - Comprehensive list of all potential risks
    2. Risk Assessment - Probability and impact analysis for each risk
    3. Mitigation Strategies - Proactive measures to reduce risk likelihood
    4. Contingency Plans - Reactive plans if risks materialize

    For each risk, include:
    - Risk ID and Category (Technical, Operational, Financial, External, etc.)
    - Risk Description
    - Probability (High/Medium/Low)
    - Impact (High/Medium/Low)
    - Risk Score/Priority
    - Mitigation Strategy
    - Contingency Plan
    - Risk Owner

    ### INSTRUCTIONS
    1. Read and analyze the context in {context_str} and **<CONTEXT** section above.
    2. Create a detailed Risk Register document covering all specified sections.
    3. Ensure clarity, completeness, and correctness in the document.
    
    ### NOTE
    1. Use Markdown format for the Risk Register document.
    2. Follow best practices for structuring Risk Registers.
    
    ### EXAMPLE OUTPUT
    Return the response in JSON format:
    {{
        "title": "Risk Register - [Project Name]",
        "executive_summary": "Overview of key risks and risk management approach",
        "risk_identification": "Comprehensive list of all identified risks with categorization",
        "risk_assessment": "Probability and impact assessment for all risks with scoring matrix",
        "mitigation_strategies": "Proactive mitigation strategies for high and medium risks",
        "contingency_plans": "Contingency plans and response strategies for critical risks",
        "detail": "Complete detailed risk register in Markdown format with sections:
                   1. Executive Summary
                   2. Risk Management Approach
                   3. Risk Identification (all risks listed by category)
                   4. Risk Assessment Matrix
                   5. Detailed Risk Analysis (each risk with full details)
                   6. Mitigation Strategies
                   7. Contingency Plans
                   8. Risk Monitoring and Control Plan"
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
        risk_data = extract_json(result_content)

        risk_response = RiskRegisterResponse(
            title=risk_data.get("title", "Risk Register"),
            executive_summary=risk_data.get("executive_summary", ""),
            risk_identification=risk_data.get("risk_identification", ""),
            risk_assessment=risk_data.get("risk_assessment", ""),
            mitigation_strategies=risk_data.get("mitigation_strategies", ""),
            contingency_plans=risk_data.get("contingency_plans", ""),
            detail=risk_data.get("detail", "")
        )

        output = RiskRegisterOutput(type="risk-register", response=risk_response)
        return {"response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error generating risk register: {e}")
        # Fallback response
        return {
            "response": {
                "title": "Risk Register",
                "executive_summary": "Error generating risk register",
                "risk_identification": "Error",
                "risk_assessment": "Error",
                "mitigation_strategies": "Error",
                "contingency_plans": "Error",
                "detail": f"Error: {str(e)}"
            }
        }

# Build LangGraph pipeline for Risk Register
workflow = StateGraph(RiskRegisterState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_risk_register", generate_risk_register)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_risk_register")
workflow.add_edge("generate_risk_register", END)

# Compile graph
risk_register_graph = workflow.compile()
