# workflows/risk_register_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.risk_register import RiskRegisterOutput, RiskRegisterResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from ..utils import extractor
class RiskRegisterState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_risk_register(state: RiskRegisterState):
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
    Business Analyst (risk management).

    ### TASK
    Create a Risk Register for: {user_message}

    ### REQUIREMENTS
    The "content" MUST be a Markdown document (use \\n) with EXACT structure:

    # Risk Register - <Project Name>

    ## 1. Executive Summary
    - Key risks overview

    ## 2. Risk Management Approach
    - Method for identification, assessment, monitoring

    ## 3. Risk Identification
    - List risks grouped by category (Technical, Operational, Financial, External)

    ## 4. Risk Assessment
    - Probability (High/Medium/Low)
    - Impact (High/Medium/Low)
    - Risk score/priority

    ## 5. Risk Register (Table)
    - Include table with columns:
    ID | Category | Description | Probability | Impact | Score | Mitigation | Contingency | Owner

    ## 6. Mitigation Strategies
    - Proactive actions for key risks

    ## 7. Contingency Plans
    - Actions if risks occur

    ## 8. Monitoring and Control
    - Tracking, review, escalation

    - Use concise bullet points
    - Do NOT leave any section empty

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Markdown document following REQUIRED structure (use \\n for newlines)",
    "summary": "One-line risk summary"
    }}

    ### RULES
    - Output JSON ONLY (no markdown wrappers, no explanations)
    - No extra keys, no missing keys
    - Do NOT change section titles or order
    - Escape \\n properly
    - All values must be strings
    """

    try:
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
        summary = "Risk Register"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "Risk Register")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating risk register: {e}")

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
