# workflows/stakeholder_register_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional, List
from models import StakeholderRegisterState
from workflows.nodes import get_chat_history, get_context_node
from connect_model import get_model_client, set_request_model_config, reset_request_model_config, MODEL
from utils import extractor
from response import success_response, error_response

def generate_stakeholder_register(state: StakeholderRegisterState, config: Optional[dict] = None):
    """Generate Stakeholder Register document using OpenRouter AI"""
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
    Business Analyst (stakeholder management, communication).

    ### TASK
    Create a Stakeholder Register for: {user_message}

    ### REQUIREMENTS
    The "content" MUST be a Markdown document (use \\n) with EXACT structure:

    # Stakeholder Register - <Project Name>

    ## 1. Document Information
    - Date, version, author

    ## 2. Executive Summary
    - Overview of key stakeholders and engagement approach

    ## 3. Stakeholder List
    - Include table with columns:
    Name | Role | Organization | Interest | Influence | Engagement Strategy | Communication | Key Concerns

    ## 4. Stakeholder Analysis Matrix
    - Include table: Stakeholder | Power | Interest | Strategy

    ## 5. Communication Plan
    - Channels, frequency, owners

    ## 6. Engagement Activities
    - Key actions per stakeholder/group

    ## 7. Risk Assessment
    - Stakeholder-related risks and mitigation

    ## 8. Conclusion

    - Use concise bullet points (except tables)
    - Do NOT leave any section empty

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Markdown document following REQUIRED structure (use \\n for newlines)",
    "summary": "One-line stakeholder summary"
    }}

    ### RULES
    - Output JSON ONLY (no markdown wrappers, no explanations)
    - No extra keys, no missing keys
    - Do NOT change section titles or order
    - Escape \\n properly
    - All values must be strings
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
        summary = "Stakeholder Register"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "Stakeholder Register")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": success_response(summary, content)
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating Stakeholder Register: {e}")
        return {
            "response": error_response("Stakeholder Register", f"Error generating Stakeholder Register: {e}")
        } # pyright: ignore[reportReturnType]
    finally:
        reset_request_model_config(token)

# Build LangGraph pipeline for Stakeholder Register
workflow = StateGraph(StakeholderRegisterState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_context_node", get_context_node)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_stakeholder_register", generate_stakeholder_register)

# Set entry point and edges
workflow.set_entry_point("get_context_node")
workflow.add_edge("get_context_node", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_stakeholder_register")
workflow.add_edge("generate_stakeholder_register", END)

# Compile graph
stakeholder_register_graph = workflow.compile()
