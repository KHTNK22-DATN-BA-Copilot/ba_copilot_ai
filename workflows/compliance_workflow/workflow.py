# workflows/compliance_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.compliance import ComplianceOutput, ComplianceResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL

class ComplianceState(TypedDict):
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

def generate_compliance(state: ComplianceState) -> ComplianceState:
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

    You are a professional Business Analyst. Create a comprehensive Compliance document
    for the following requirement: {user_message}

    Analyze all legal and regulatory compliance requirements including:
    1. Regulatory Requirements - Industry-specific regulations and standards
    2. Legal Requirements - Applicable laws and legal obligations
    3. Compliance Status - Current compliance level and gaps
    4. Recommendations - Actions needed to achieve full compliance

    Consider various compliance domains:
    - Data Privacy (GDPR, CCPA, etc.)
    - Industry Standards (ISO, SOC 2, PCI-DSS, HIPAA, etc.)
    - Accessibility (WCAG, ADA, etc.)
    - Security Standards
    - Local and International Laws

    Return the response in JSON format:
    {{
        "title": "Compliance Document - [Project Name]",
        "executive_summary": "Overview of compliance requirements and current status",
        "regulatory_requirements": "Detailed analysis of all applicable regulatory requirements and standards",
        "legal_requirements": "Legal obligations, contracts, and statutory requirements",
        "compliance_status": "Current compliance status assessment with identified gaps",
        "recommendations": "Recommended actions, timeline, and implementation plan for compliance",
        "detail": "Complete detailed compliance document in Markdown format with sections:
                   1. Executive Summary
                   2. Scope and Applicability
                   3. Regulatory Requirements (detailed breakdown)
                   4. Legal Requirements and Obligations
                   5. Compliance Status Assessment
                   6. Gap Analysis
                   7. Compliance Roadmap and Implementation Plan
                   8. Monitoring and Maintenance Plan
                   9. Recommendations and Next Steps"
    }}

    Return only JSON, no additional text.
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
        compliance_data = extract_json(result_content)

        compliance_response = ComplianceResponse(
            title=compliance_data.get("title", "Compliance Document"),
            executive_summary=compliance_data.get("executive_summary", ""),
            regulatory_requirements=compliance_data.get("regulatory_requirements", ""),
            legal_requirements=compliance_data.get("legal_requirements", ""),
            compliance_status=compliance_data.get("compliance_status", ""),
            recommendations=compliance_data.get("recommendations", ""),
            detail=compliance_data.get("detail", "")
        )

        output = ComplianceOutput(type="compliance", response=compliance_response)
        return {"response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error generating compliance document: {e}")
        # Fallback response
        return {
            "response": {
                "title": "Compliance Document",
                "executive_summary": "Error generating compliance document",
                "regulatory_requirements": "Error",
                "legal_requirements": "Error",
                "compliance_status": "Error",
                "recommendations": "Error",
                "detail": f"Error: {str(e)}"
            }
        }

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
