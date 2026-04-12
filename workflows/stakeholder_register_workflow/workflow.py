# workflows/stakeholder_register_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from ..utils import extractor
class StakeholderRegisterState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_stakeholder_register(state: StakeholderRegisterState):
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
        summary = "Stakeholder Register"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "Stakeholder Register")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating Stakeholder Register: {e}")

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
