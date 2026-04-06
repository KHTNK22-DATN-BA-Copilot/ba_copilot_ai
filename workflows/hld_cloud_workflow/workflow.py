# workflows/hld_cloud_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.hld_cloud import HLDCloudOutput, HLDCloudResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from ..utils import extractor
class HLDCloudState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_hld_cloud(state: HLDCloudState):
    """Generate Cloud Infrastructure Setup document using OpenRouter AI"""
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
    Senior Cloud Architect (scalable, secure, cost-optimized systems).

    ### TASK
    Design a Cloud Infrastructure Setup for: {user_message}

    ### REQUIREMENTS
    The "content" MUST be a Markdown document (use \\n) with EXACT structure and order:

    1. Title:
    # Cloud Infrastructure Setup - <Project Name>

    2. Sections:
    ## 1. Executive Summary
    - 1–2 sentence overview

    ## 2. Cloud Provider Selection
    - Provider choice + brief justification

    ## 3. Infrastructure Components
    - Compute, storage, database, networking, services

    ## 4. Network Architecture
    - VPC/VNet, subnets, routing, gateways

    ## 5. Deployment Architecture
    - Regions, AZs, high availability, disaster recovery

    ## 6. Scalability Strategy
    - Auto-scaling, load balancing, CDN, caching

    ## 7. Security Architecture
    - IAM, encryption, network security, compliance

    ## 8. Cost Estimation
    - Cost breakdown + optimization strategies

    ## 9. Monitoring and Operations
    - Logging, monitoring, alerting

    - Use concise bullet points
    - Use concrete cloud services where applicable

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Markdown document following REQUIRED structure (use \\n for newlines)",
    "summary": "One-line architecture summary"
    }}

    ### RULES
    - Output JSON ONLY (no markdown wrappers, no explanations)
    - No extra keys, no missing keys
    - Do NOT change section titles or order
    - Escape \\n properly
    - Be concise but complete
    """

    try:
        raw_output = model_client.gemini_completion(prompt)

        json_data = extractor.extract_json(raw_output)
        summary = "HLD Cloud"
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "HLD Cloud")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating cloud infrastructure setup: {e}")
        

# Build LangGraph pipeline for Cloud Infrastructure Setup
workflow = StateGraph(HLDCloudState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_hld_cloud", generate_hld_cloud)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_hld_cloud")
workflow.add_edge("generate_hld_cloud", END)

# Compile graph
hld_cloud_graph = workflow.compile()
