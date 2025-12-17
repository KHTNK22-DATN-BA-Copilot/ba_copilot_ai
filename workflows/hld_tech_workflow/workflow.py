# workflows/hld_tech_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.hld_tech import HLDTechOutput, HLDTechResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL

class HLDTechState(TypedDict):
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

def generate_hld_tech(state: HLDTechState) -> HLDTechState:
    """Generate Tech Stack Selection document using OpenRouter AI"""
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

    You are a professional Technical Architect. Create a comprehensive Technology Stack Selection document
    for the following requirement: {user_message}

    Provide detailed technology selection covering:
    1. Frontend Technologies - Framework, libraries, UI components, state management
    2. Backend Technologies - Programming language, frameworks, API design
    3. Database Selection - Primary database, caching, data warehousing
    4. Infrastructure Tools - CI/CD, monitoring, logging, containerization
    5. Justification - Why each technology was selected (performance, scalability, team expertise, community support, cost)
    6. Alternatives Considered - Other options evaluated and why they were not chosen

    Return the response in JSON format with ALL FIELDS AS STRINGS (no nested objects or arrays):
    {{
        "title": "Technology Stack Selection - [Project Name]",
        "executive_summary": "Overview of selected technology stack and key architectural decisions",
        "frontend_technologies": "Frontend framework (React/Vue/Angular), state management, UI libraries, build tools, testing frameworks",
        "backend_technologies": "Programming language (Node.js/Python/Java), framework (Express/Django/Spring), API design (REST/GraphQL), authentication",
        "database_selection": "Primary database (PostgreSQL/MongoDB/MySQL), caching (Redis/Memcached), search (Elasticsearch), data warehouse",
        "infrastructure_tools": "Containerization (Docker/Kubernetes), CI/CD (GitHub Actions/Jenkins), monitoring (Prometheus/Grafana), logging (ELK)",
        "justification": "MUST BE A STRING - Detailed justification for each technology choice including: technical fit, performance characteristics, scalability, team expertise, community support, licensing, total cost of ownership",
        "alternatives_considered": "MUST BE A STRING - Alternative technologies evaluated with pros/cons comparison and decision rationale",
        "detail": "Complete detailed tech stack document in Markdown format with sections:
                   1. Executive Summary
                   2. Technology Stack Overview
                   3. Frontend Technology Stack
                      - Framework and Libraries
                      - State Management
                      - UI Components
                      - Build and Development Tools
                   4. Backend Technology Stack
                      - Programming Language and Framework
                      - API Design and Architecture
                      - Authentication and Authorization
                      - Background Job Processing
                   5. Database and Data Layer
                      - Primary Database Selection
                      - Caching Strategy
                      - Search and Analytics
                      - Data Migration Tools
                   6. DevOps and Infrastructure
                      - Containerization and Orchestration
                      - CI/CD Pipeline
                      - Monitoring and Logging
                      - Infrastructure as Code
                   7. Third-Party Services and Integrations
                   8. Technology Justification Matrix
                   9. Alternatives Considered
                   10. Technology Risks and Mitigation
                   11. Team Training and Onboarding Plan"
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
        tech_data = extract_json(result_content)

        tech_response = HLDTechResponse(
            title=tech_data.get("title", "Technology Stack Selection"),
            executive_summary=tech_data.get("executive_summary", ""),
            frontend_technologies=tech_data.get("frontend_technologies", ""),
            backend_technologies=tech_data.get("backend_technologies", ""),
            database_selection=tech_data.get("database_selection", ""),
            infrastructure_tools=tech_data.get("infrastructure_tools", ""),
            justification=tech_data.get("justification", ""),
            alternatives_considered=tech_data.get("alternatives_considered", ""),
            detail=tech_data.get("detail", "")
        )

        output = HLDTechOutput(type="hld-tech", response=tech_response)
        return {"response": output.model_dump()["response"]}

    except Exception as e:
        print(f"Error generating tech stack selection: {e}")
        # Fallback response
        return {
            "response": {
                "title": "Technology Stack Selection",
                "executive_summary": "Error generating tech stack selection",
                "frontend_technologies": "Error",
                "backend_technologies": "Error",
                "database_selection": "Error",
                "infrastructure_tools": "Error",
                "justification": "Error",
                "alternatives_considered": "Error",
                "detail": f"Error: {str(e)}"
            }
        }

# Build LangGraph pipeline for Tech Stack Selection
workflow = StateGraph(HLDTechState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_hld_tech", generate_hld_tech)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_hld_tech")
workflow.add_edge("generate_hld_tech", END)

# Compile graph
hld_tech_graph = workflow.compile()
