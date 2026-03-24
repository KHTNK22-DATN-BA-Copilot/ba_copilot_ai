# workflows/compliance_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.compliance import ComplianceOutput, ComplianceResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from ..utils import extractor
class ComplianceState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_compliance(state: ComplianceState):
    """Generate Compliance document using OpenRouter AI"""
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
    Professional Business Analyst (Compliance).

    ### TASK
    Create a Compliance document for: {user_message}

    ### REQUIREMENTS
    Cover:
    - Regulatory requirements (industry standards)
    - Legal obligations (laws, contracts)
    - Compliance status (current state + gaps)
    - Recommendations (actions, timeline)

    Consider:
    - Data Privacy (GDPR, CCPA)
    - Industry Standards (ISO, SOC 2, PCI-DSS, HIPAA)
    - Accessibility (WCAG, ADA)
    - Security standards
    - Local & international laws

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Markdown compliance document with sections below",
    "summary": "One-line concise compliance overview"
    }}

    ### REQUIRED STRUCTURE (Markdown)
    # Compliance Document
    ## Executive Summary
    ## Scope and Applicability
    ## Regulatory Requirements
    ## Legal Requirements
    ## Compliance Status
    ## Gap Analysis
    ## Compliance Roadmap
    ## Monitoring and Maintenance
    ## Recommendations

    ### RULES
    - Return ONLY valid JSON (no markdown wrapper, no extra text)
    - Use clear, structured Markdown
    - Keep content concise but complete
    - Ensure JSON is parsable (escape \\n properly)
    """

    try:
        # Use OpenRouter (default)
        completion = model_client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL
        )
        raw_output = completion.choices[0].message.content

        # Use Gemini 2.5 Flash Lite
        raw_output = model_client.gemini_completion(prompt)

        json_data = extractor.extract_json(raw_output)
        summary = "Compliance"
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "Compliance")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]

    except Exception as e:
        print(f"Error generating compliance document: {e}")

# Build LangGraph pipeline for Compliance
workflow = StateGraph(ComplianceState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_compliance", generate_compliance)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_compliance")
workflow.add_edge("generate_compliance", END)

# Compile graph
compliance_graph = workflow.compile()
