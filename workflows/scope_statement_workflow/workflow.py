# workflows/scope_statement_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.scope_statement import ScopeStatementOutput, ScopeStatementResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client
from ..utils import extractor

class ScopeStatementState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_scope_statement(state: ScopeStatementState):
    """Generate Scope Statement document using OpenRouter AI"""
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
    Business Analyst (scope definition, stakeholder alignment).

    ### TASK
    Create a Project Scope Statement for: {user_message}

    ### REQUIREMENTS
    The "content" MUST be a Markdown document (use \\n) with EXACT structure:

    # Project Scope Statement - <Project Name>

    ## 1. Document Control
    - Version, date, approval

    ## 2. Project Overview
    ### 2.1 Purpose
    ### 2.2 Description
    ### 2.3 Justification

    ## 3. Project Scope
    ### 3.1 In Scope
    ### 3.2 Out of Scope

    ## 4. Deliverables
    ### 4.1 Major Deliverables
    - Include table: Deliverable | Description | Acceptance Criteria

    ### 4.2 Milestones
    - Include table: Milestone | Target Date | Description

    ## 5. Requirements Summary
    ### 5.1 Functional
    ### 5.2 Non-Functional
    ### 5.3 Technical

    ## 6. Constraints
    ## 7. Assumptions

    ## 8. Dependencies
    ### 8.1 Internal
    ### 8.2 External

    ## 9. Success Criteria
    ### 9.1 Project Success
    ### 9.2 Acceptance Criteria

    ## 10. Stakeholders
    - Include table: Stakeholder | Role | Responsibility

    ## 11. Change Management
    - Scope change process

    ## 12. Risks and Issues

    ## 13. Approval
    - Include table: Role | Name | Signature | Date

    - Use concise bullet points (except tables)
    - Do NOT leave any section empty

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Markdown document following REQUIRED structure (use \\n for newlines)",
    "summary": "One-line scope summary"
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
        summary = "Scope Statement"
        content = ""
        if not json_data:
            print("No JSON data found! Returning raw output...")
            content = raw_output
        else:
            summary = json_data.get("summary", "Scope Statement")
            content = json_data.get("content", "Empty json_data")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating Scope Statement: {e}")

# Build LangGraph pipeline for Scope Statement
workflow = StateGraph(ScopeStatementState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_scope_statement", generate_scope_statement)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_scope_statement")
workflow.add_edge("generate_scope_statement", END)

# Compile graph
scope_statement_graph = workflow.compile()
