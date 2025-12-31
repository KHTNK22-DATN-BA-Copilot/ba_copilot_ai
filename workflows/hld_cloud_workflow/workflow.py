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

class HLDCloudState(TypedDict):
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

def generate_hld_cloud(state: HLDCloudState) -> HLDCloudState:
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
    You are a professional Cloud Architect. With strong expertise in designing scalable, secure, and cost-effective cloud infrastructure solutions.
    
    ### CONTEXT
    Create a comprehensive Cloud Infrastructure Setup document for the following requirement: {user_message}

    Provide detailed cloud infrastructure planning including:
    1. Cloud Provider Selection - AWS, Azure, GCP, or hybrid approach with justification
    2. Infrastructure Components - Compute, storage, networking, databases, services
    3. Deployment Architecture - Regions, availability zones, disaster recovery
    4. Scalability Strategy - Auto-scaling, load balancing, CDN
    5. Security Considerations - IAM, encryption, network security, compliance
    6. Cost Estimation - Infrastructure costs, cost optimization strategies

    ### INSTRUCTIONS
    1. Read and analyze the context in {context_str} and **<CONTEXT** section above.
    2. Create a comprehensive Cloud Infrastructure Setup document covering all specified sections.
    3. Ensure clarity, completeness, and correctness in the document.
    
    ### NOTE
    1. Use Markdown format for the Cloud Infrastructure Setup document.
    2. Follow best practices for structuring cloud architecture documentation.
    
    ### EXAMPLE OUTPUT
    Return the response in JSON format:
    {{
        "title": "Cloud Infrastructure Setup - [Project Name]",
        "executive_summary": "Brief overview of cloud infrastructure approach and key decisions",
        "cloud_provider_selection": "Selected cloud provider(s) with detailed justification and comparison",
        "infrastructure_components": "Detailed list of all cloud services and components (compute instances, databases, storage, networking, etc.)",
        "deployment_architecture": "Multi-region/zone architecture, high availability setup, disaster recovery plan",
        "scalability_strategy": "Auto-scaling policies, load balancing strategy, performance optimization",
        "security_considerations": "IAM roles, encryption (at-rest/in-transit), network security, compliance certifications",
        "cost_estimation": "Estimated monthly/annual costs with breakdown by service, cost optimization recommendations",
        "detail": "Complete detailed cloud infrastructure document in Markdown format with sections:
                   1. Executive Summary
                   2. Cloud Provider Selection and Justification
                   3. Infrastructure Components Specification
                   4. Network Architecture Design
                   5. Deployment Architecture (Multi-region/AZ strategy)
                   6. Scalability and Performance Strategy
                   7. Security Architecture and Compliance
                   8. Disaster Recovery and Business Continuity
                   9. Cost Analysis and Optimization
                   10. Migration Strategy (if applicable)
                   11. Monitoring and Operations Plan"
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
        cloud_data = extract_json(result_content)

        cloud_response = HLDCloudResponse(
            title=cloud_data.get("title", "Cloud Infrastructure Setup"),
            executive_summary=cloud_data.get("executive_summary", ""),
            cloud_provider_selection=cloud_data.get("cloud_provider_selection", ""),
            infrastructure_components=cloud_data.get("infrastructure_components", ""),
            deployment_architecture=cloud_data.get("deployment_architecture", ""),
            scalability_strategy=cloud_data.get("scalability_strategy", ""),
            security_considerations=cloud_data.get("security_considerations", ""),
            cost_estimation=cloud_data.get("cost_estimation", ""),
            detail=cloud_data.get("detail", "")
        )

        output = HLDCloudOutput(type="hld-cloud", response=cloud_response)
        return {"response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error generating cloud infrastructure setup: {e}")
        # Fallback response
        return {
            "response": {
                "title": "Cloud Infrastructure Setup",
                "executive_summary": "Error generating cloud infrastructure setup",
                "cloud_provider_selection": "Error",
                "infrastructure_components": "Error",
                "deployment_architecture": "Error",
                "scalability_strategy": "Error",
                "security_considerations": "Error",
                "cost_estimation": "Error",
                "detail": f"Error: {str(e)}"
            }
        }

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
