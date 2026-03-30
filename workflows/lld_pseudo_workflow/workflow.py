"""
LLD Pseudocode Workflow
Generates algorithm pseudocode and logic flow documentation.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List
import json
import logging
from workflows.nodes import get_chat_history, get_content_file
from connect_model import get_model_client, MODEL
from models.lld_pseudo import LLDPseudoResponse, LLDPseudoOutput
import re
from ..utils import extractor

logger = logging.getLogger(__name__)

class LLDPseudoState(TypedDict):
    """State for LLD Pseudocode workflow"""
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List[str]]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_lld_pseudocode(state: LLDPseudoState):
    """
    Generate algorithm pseudocode document using LLM.
    Creates detailed pseudocode with complexity analysis and implementation notes.
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
        Algorithm Designer (pseudocode, analysis).

        ### TASK
        Create a Pseudocode Design for: {user_message}

        ### REQUIREMENTS
        The "content" MUST be a Markdown document (use \\n) with EXACT structure:

        # Pseudocode - <Algorithm Name>

        ## 1. Overview
        - Problem, goal, approach

        ## 2. Input / Output
        - Inputs, outputs, preconditions, postconditions

        ## 3. Pseudocode
        - Use standard notation: FUNCTION, BEGIN, END, IF, ELSE, FOR, WHILE, RETURN
        - Clear structure, proper indentation
        - Include helper functions if needed

        ## 4. Complexity Analysis
        - Time and space (Big-O)
        - Best, average, worst cases (brief justification)

        ## 5. Edge Cases
        - Boundary conditions, errors, special cases

        ## 6. Implementation Notes
        - Data structures, optimizations, pitfalls

        - Use concise bullet points (except pseudocode)
        - Ensure clarity and correctness

        ### OUTPUT (STRICT JSON ONLY)
        {{
        "content": "Markdown document following REQUIRED structure (use \\n for newlines)",
        "summary": "One-line algorithm summary"
        }}

        ### RULES
        - Output JSON ONLY (no markdown wrappers, no explanations)
        - No extra keys, no missing keys
        - Do NOT change section titles or order
        - Escape \\n properly
        - All values must be strings
        """

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
        summary = "LLD Pseudo"
        content = ""
        if not json_data:
            print("No JSON data found returning raw output")
            content = json_data
        else:
            summary = json_data.get("summary", "LLD Pseudo")
            content = json_data.get("content", "")
        return {
            "response": {
                "summary": summary,
                "content": content
            }
        } # pyright: ignore[reportReturnType]

    except Exception as e:
        logger.error(f"Error generating pseudocode: {e}")

# Build LangGraph pipeline for LLD Pseudocode
workflow = StateGraph(LLDPseudoState)

# Add nodes in sequence: Get Content File -> Chat History -> Generate
workflow.add_node("get_content_file", get_content_file)
workflow.add_node("get_chat_history", get_chat_history)
workflow.add_node("generate_lld_pseudo", generate_lld_pseudocode)

# Set entry point and edges
workflow.set_entry_point("get_content_file")
workflow.add_edge("get_content_file", "get_chat_history")
workflow.add_edge("get_chat_history", "generate_lld_pseudo")
workflow.add_edge("generate_lld_pseudo", END)

# Compile graph
lld_pseudo_graph = workflow.compile()
