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

logger = logging.getLogger(__name__)

class LLDPseudoState(TypedDict):
    """State for LLD Pseudocode workflow"""
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List[str]]
    extracted_text: Optional[str]
    chat_context: Optional[str]

def generate_lld_pseudocode(state: LLDPseudoState) -> LLDPseudoState:
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

    You are a professional Algorithm Designer. Create comprehensive Pseudocode documentation
    for the following requirement: {user_message}

    Provide detailed pseudocode covering:
    1. Algorithm Overview - Purpose, problem statement, approach
    2. Input/Output Specification - Input parameters, output format, preconditions, postconditions
    3. Pseudocode - Step-by-step algorithm logic in structured pseudocode format
    4. Complexity Analysis - Time complexity, space complexity, best/average/worst case
    5. Edge Cases - Boundary conditions, error cases, special scenarios
    6. Implementation Notes - Language-specific considerations, optimization opportunities

    Return the response in JSON format with ALL FIELDS AS STRINGS (no nested objects or arrays):
    {{
        "title": "Pseudocode - [Algorithm Name]",
        "algorithm_overview": "Complete algorithm overview including problem description, solution approach, key insights, algorithmic paradigm (divide-and-conquer, dynamic programming, greedy, etc.)",
        "input_output": "Detailed input/output specification with parameter names, data types, ranges, preconditions (what must be true before), postconditions (what will be true after), example inputs and outputs",
        "pseudocode": "MUST BE A STRING - Complete step-by-step pseudocode using standard pseudocode notation (FUNCTION, BEGIN, END, IF, ELSE, FOR, WHILE, RETURN). Include variable declarations, loop structures, conditional logic, function calls. Format with proper indentation.",
        "complexity_analysis": "Comprehensive complexity analysis including: Time complexity (Big O notation), Space complexity (Big O notation), Best case, Average case, Worst case scenarios, Justification for each complexity measure",
        "edge_cases": "Identification and handling of edge cases: empty input, single element, duplicate values, negative numbers, null/undefined, overflow conditions, boundary values, error conditions",
        "implementation_notes": "Practical implementation guidance: language-specific optimizations, data structure choices, library functions, common pitfalls, performance tuning tips, testing strategies",
        "detail": "Complete detailed pseudocode document in Markdown format with sections:
                   1. Algorithm Overview
                   2. Problem Statement
                   3. Solution Approach
                   4. Input/Output Specification
                   5. Pseudocode
                      - Main algorithm
                      - Helper functions
                      - Data structures
                   6. Example Walkthrough
                   7. Complexity Analysis
                      - Time Complexity Derivation
                      - Space Complexity Derivation
                   8. Edge Cases and Error Handling
                   9. Implementation Considerations
                   10. Optimization Opportunities
                   11. Testing Strategy
                   12. References and Further Reading"
    }}

    Ensure:
    - Pseudocode uses clear, consistent notation
    - All variables and functions are well-named
    - Logic flow is easy to follow
    - Edge cases are comprehensive
    - Complexity analysis is mathematically justified

    Return only valid JSON, no additional text.
    """

        completion = model_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Algorithm Designer who creates clear, detailed pseudocode with comprehensive analysis."
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
            pseudo_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            # Fallback response
            pseudo_data = {
                "title": "Pseudocode Document",
                "algorithm_overview": "Error parsing response",
                "input_output": "Error",
                "pseudocode": "Error",
                "complexity_analysis": "Error",
                "edge_cases": "Error",
                "implementation_notes": "Error",
                "detail": f"Error generating pseudocode: {str(e)}"
            }

        # Create response using Pydantic model
        pseudo_response = LLDPseudoResponse(**pseudo_data)
        output = LLDPseudoOutput(type="lld-pseudo", response=pseudo_response)

        return {"response": output.model_dump()["response"]}

    except Exception as e:
        logger.error(f"Error generating pseudocode: {e}")
        # Fallback response
        return {
            "response": {
                "title": "Pseudocode Document",
                "algorithm_overview": "Error generating pseudocode",
                "input_output": "Error",
                "pseudocode": "Error",
                "complexity_analysis": "Error",
                "edge_cases": "Error",
                "implementation_notes": "Error",
                "detail": f"Error: {str(e)}"
            }
        }

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
