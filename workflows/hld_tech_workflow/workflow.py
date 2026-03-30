# workflows/hld_tech_workflow/workflow.py
from langgraph.graph import StateGraph, END
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.hld_tech import HLDTechOutput, HLDTechResponse
from typing import TypedDict, Optional, List
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from ..utils import extractor

class HLDTechState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_hld_tech(state: HLDTechState):
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

    ### ROLE
    Senior Technical Architect (tech stack selection for scalable, maintainable systems).

    ### TASK
    Design a Technology Stack Selection for: {user_message}

    ### REQUIREMENTS
    The "content" MUST be a Markdown document (use \\n) with EXACT structure:

    # Technology Stack Selection - <Project Name>

    ## 1. Executive Summary
    - 1–2 sentence overview

    ## 2. Frontend Technologies
    - Framework, state management, UI, tools

    ## 3. Backend Technologies
    - Language, framework, API design, auth

    ## 4. Database and Data Layer
    - Primary DB, caching, search, analytics

    ## 5. Infrastructure and DevOps
    - CI/CD, containerization, monitoring, logging

    ## 6. Technology Justification
    - Why each key tech is chosen (performance, scalability, cost, team fit)

    ## 7. Alternatives Considered
    - Key alternatives + brief rejection reasons

    - Use concise bullet points
    - Use concrete technologies (e.g., React, Node.js, PostgreSQL, Docker)

    ### OUTPUT (STRICT JSON ONLY)
    {{
    "content": "Markdown document following REQUIRED structure (use \\n for newlines)",
    "summary": "One-line tech stack summary"
    }}

    ### RULES
    - Output JSON ONLY (no markdown wrappers, no explanations)
    - No extra keys, no missing keys
    - Do NOT change section titles or order
    - Escape \\n properly
    - Be concise but complete
    """
    try:
        # Use OpenRouter (default)
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
        summary = "HLD Tech"
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "HLD Tech")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]
    except Exception as e:
        print(f"Error generating tech stack selection: {e}")

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
