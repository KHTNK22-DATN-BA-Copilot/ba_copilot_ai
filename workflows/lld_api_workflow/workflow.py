"""
LLD API Specifications Workflow
Generates detailed API endpoint specifications in OpenAPI/Swagger format.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List
import json
import logging
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from models.lld_api import LLDAPIResponse, LLDAPIOutput

logger = logging.getLogger(__name__)

class LLDAPIState(TypedDict):
    """State for LLD API Specifications workflow"""
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List[str]]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_lld_api_specs(state: LLDAPIState) -> LLDAPIState:
    """
    Generate detailed API specifications document using LLM.
    Creates comprehensive API documentation with endpoints, models, authentication.
    """
    try:
        model_client = get_model_client()
        
        # Extract context
        user_message = state.get('user_message', '')
        extracted_text = state.get('extracted_text', '')
        chat_context = state.get('chat_context', '')
        
        # Build context string
        context_str = ""
        if chat_context:
            context_str += f"Context from previous conversation:\n{chat_context}\n\n"
        if extracted_text:
            context_str += f"Extracted content from uploaded files:\n{extracted_text}\n\n"

        prompt = f"""
    {context_str}

    ### ROLE
    You are a professional API Architect. With strong expertise in designing and documenting RESTful APIs following OpenAPI/Swagger standards.
    
    ### CONTEXT
    Create comprehensive API Specifications document for the following requirement: {user_message}

    Provide detailed API specifications covering:
    1. API Overview - Purpose, base URL, supported formats
    2. Authentication - Auth methods, token management, security
    3. Endpoints - All REST endpoints with methods, paths, parameters, request/response examples
    4. Data Models - Request/response schemas, data types, validation rules
    5. Error Handling - Error codes, error messages, error response format
    6. Rate Limiting - Request limits, throttling policies
    7. Versioning - API versioning strategy, deprecation policy

    ### INSTRUCTIONS
    1. Read and analyze the context in {context_str} and **<CONTEXT** section above.
    2. Create a comprehensive API Specifications document covering all specified sections.
    3. Ensure clarity, completeness, and correctness in the document.
    
    ### NOTE
    1. Use Markdown format for the API Specifications document.
    2. Follow OpenAPI/Swagger best practices for structuring API documentation.
    
    ### EXAMPLE OUTPUT
    Return the response in JSON format with ALL FIELDS AS STRINGS (no nested objects or arrays):
    {{
        "title": "API Specifications - [Project Name]",
        "api_overview": "Complete API overview including purpose, architecture style (REST/GraphQL), base URL, supported response formats (JSON/XML), API design principles",
        "authentication": "Detailed authentication mechanisms (OAuth 2.0, JWT, API Keys), token lifecycle, refresh tokens, security best practices, HTTPS requirements",
        "endpoints": "MUST BE A STRING - Comprehensive list of all API endpoints with: HTTP method, path, description, request parameters (path/query/body), request examples, response examples, status codes, pagination details. Format as markdown table or structured text.",
        "data_models": "MUST BE A STRING - All request and response data models with field names, data types, required/optional, validation rules, example values. Include common models used across endpoints.",
        "error_handling": "Error response format, standard error codes (400, 401, 403, 404, 500), error messages, troubleshooting guide",
        "rate_limiting": "Rate limit policies (requests per minute/hour), throttling behavior, rate limit headers, upgrade options for higher limits",
        "versioning": "API versioning strategy (URL path, header, query parameter), current version, deprecation policy, migration guides",
        "detail": "Complete detailed API specifications document in Markdown format with sections:
                   1. Introduction and Overview
                   2. Getting Started
                   3. Authentication and Authorization
                   4. API Endpoints Reference
                      - User Management Endpoints
                      - Resource CRUD Endpoints
                      - Search and Filter Endpoints
                   5. Request/Response Formats
                   6. Data Models and Schemas
                   7. Error Handling
                   8. Rate Limiting and Quotas
                   9. Versioning and Deprecation
                   10. Code Examples (cURL, JavaScript, Python)
                   11. Changelog
                   12. Support and Resources"
    }}

    Ensure:
    - All endpoint descriptions include full OpenAPI/Swagger style documentation
    - Request/response examples in JSON format
    - Complete parameter documentation
    - Status code explanations
    - Security requirements for each endpoint
    """

        completion = model_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert API Architect who creates comprehensive API documentation following OpenAPI/Swagger standards."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL
        )

        response_text = completion.choices[0].message.content.strip()

        # Extract JSON from markdown code blocks if present
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()

        # Parse JSON response
        try:
            api_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            # Fallback response
            api_data = {
                "title": "API Specifications",
                "api_overview": "Error parsing response",
                "authentication": "Error",
                "endpoints": "Error",
                "data_models": "Error",
                "error_handling": "Error",
                "rate_limiting": "Error",
                "versioning": "Error",
                "detail": f"Error generating API specifications: {str(e)}"
            }

        # Create response using Pydantic model
        api_response = LLDAPIResponse(**api_data)
        output = LLDAPIOutput(type="lld-api", response=api_response)

        return {"response": output.model_dump()["response"]}

    except Exception as e:
        logger.error(f"Error generating API specifications: {e}")
        # Fallback response
        return {
            "response": {
                "title": "API Specifications",
                "api_overview": "Error generating API specifications",
                "authentication": "Error",
                "endpoints": "Error",
                "data_models": "Error",
                "error_handling": "Error",
                "rate_limiting": "Error",
                "versioning": "Error",
                "detail": f"Error: {str(e)}"
            }
        }

# Build LangGraph pipeline for LLD API Specifications
workflow = StateGraph(LLDAPIState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_lld_api", generate_lld_api_specs)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_lld_api")
workflow.add_edge("generate_lld_api", END)

# Compile graph
lld_api_graph = workflow.compile()
