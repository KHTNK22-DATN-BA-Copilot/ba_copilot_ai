# workflows/metadata_extraction_workflow/workflow.py
"""
Metadata Extraction Workflow

This workflow analyzes markdown content to detect which BA document types
are present and extract their line ranges. It uses phase-based nodes to
efficiently process document type detection across different categories.
"""

from langgraph.graph import StateGraph, END
import sys
import os
import json
import re
from typing import TypedDict, Optional, List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from connect_model import get_model_client, MODEL
from models.metadata_extraction import (
    MetadataExtractionResponse,
    DocumentTypeMetadata,
    ALL_DOCUMENT_TYPES,
    DOCUMENT_TYPE_DESCRIPTIONS,
    PHASE_1_PROJECT_INITIATION,
    PHASE_2_BUSINESS_PLANNING,
    PHASE_3_FEASIBILITY_RISK,
    PHASE_4_HIGH_LEVEL_DESIGN,
    PHASE_5_LOW_LEVEL_DESIGN,
    PHASE_6_UIUX_DESIGN,
    PHASE_7_TESTING_QA,
    ADDITIONAL_DOCUMENT_TYPES,
)


# ============================================================================
# State Definition
# ============================================================================

class MetadataExtractionState(TypedDict):
    """State for the metadata extraction workflow."""
    document_id: str
    content: str
    filename: Optional[str]
    total_lines: int
    # Results from each phase node
    phase1_results: Optional[List[Dict]]
    phase2_results: Optional[List[Dict]]
    phase3_results: Optional[List[Dict]]
    phase4_results: Optional[List[Dict]]
    phase5_results: Optional[List[Dict]]
    phase6_results: Optional[List[Dict]]
    phase7_results: Optional[List[Dict]]
    additional_results: Optional[List[Dict]]
    # Final aggregated response
    response: Optional[Dict]


# ============================================================================
# Helper Functions
# ============================================================================

def extract_json_arr_from_response(text: str) -> List[Dict]:
    """
    Extract JSON array from LLM response text.
    
    Args:
        text: Raw LLM response text
        
    Returns:
        List of dicts with document type metadata
    """
    try:
        # Clean up the response - remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        # Try to find JSON array
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end > start:
            json_str = text[start:end]
            return json.loads(json_str)
        
        # Try to find JSON object (single result)
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            json_str = text[start:end]
            result = json.loads(json_str)
            # If it's a wrapper object with "results" key
            if "results" in result:
                return result["results"]
            return [result]
            
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return []


def build_phase_prompt(content: str, doc_types: List[str], total_lines: int) -> str:
    """
    Build a prompt for detecting specific document types in content.
    
    Args:
        content: The markdown content to analyze
        doc_types: List of document type IDs to detect
        total_lines: Total number of lines in the content
        
    Returns:
        Formatted prompt string
    """
    type_descriptions = "\n".join([
        f"- {dt}: {DOCUMENT_TYPE_DESCRIPTIONS.get(dt, dt)}"
        for dt in doc_types
    ])
    
    # Truncate content if too long (keep first and last parts)
    max_content_length = 150000
    if len(content) > max_content_length:
        half = max_content_length // 2
        content = content[:half] + "\n\n[... content truncated ...]\n\n" + content[-half:]
    
    prompt = f"""You are an expert document analyst. Analyze the following markdown content and determine if any of these BA (Business Analysis) document types are present.

DOCUMENT TYPES TO DETECT:
{type_descriptions}

IMPORTANT RULES:
1. For each document type, if found, provide the line_start (1-indexed) and line_end (1-indexed) where that section exists
2. If a document type is NOT found, use line_start: -1 and line_end: -1
3. The document has {total_lines} total lines
4. Look for section headers, content patterns, and document structure to identify document types
5. A document type is considered present if there's a substantial section (not just a brief mention)

CONTENT TO ANALYZE:
```markdown
{content}
```

Return ONLY a JSON array with this exact format (no other text):
[
  {{"type": "document-type-id", "line_start": <number>, "line_end": <number>}},
  ...
]

Include ALL document types listed above in your response, even if not found (use -1 values for those not found).
"""
    return prompt


def call_llm_for_phase(content: str, doc_types: List[str], total_lines: int) -> List[Dict]:
    """
    Call LLM to detect document types for a specific phase.
    
    Args:
        content: The markdown content
        doc_types: Document types to detect
        total_lines: Total lines in content
        
    Returns:
        List of detection results
    """
    if not doc_types:
        return []
    
    model_client = get_model_client()
    prompt = build_phase_prompt(content, doc_types, total_lines)
    
    try:
        completion = model_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a precise document analyzer. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model=MODEL
        )
        
        response_text = completion.choices[0].message.content or ""
        results = extract_json_arr_from_response(response_text)
        
        # NOTE: Missing types will be filled in by aggregate_results node
        # Each phase only returns what LLM actually detected
        return results
    except Exception as e:
        print(f"Error calling LLM: {e}")
        # Return not-found for all types on error
        # because it just means we fail to extract metadata, the backend should interpret and instruct further
        return [{"type": dt, "line_start": -1, "line_end": -1} for dt in doc_types]


# ============================================================================
# Workflow Nodes
# ============================================================================

def initialize_state(state: MetadataExtractionState) -> MetadataExtractionState:
    """Initialize state with line count."""
    content = state.get("content", "")
    lines = content.split('\n')
    state["total_lines"] = len(lines)
    return state

# NOTE: CURRENTLY, ALL PHASES' CONTENT IS JUST THE INITIAL CONTENT (NO CONTENT-CHAINING, NO INTERDEPENDENCE BETWEEN DOCS YET)
# TODO IMPLEMENT DEPENDENCIES BETWEEN PHASES, HANDLE LOGIC
def detect_phase1_documents(state: MetadataExtractionState) -> MetadataExtractionState:
    """Detect Phase 1: Project Initiation documents."""
    results = call_llm_for_phase(
        state["content"],
        PHASE_1_PROJECT_INITIATION,
        state["total_lines"]
    )
    state["phase1_results"] = results
    return state


def detect_phase2_documents(state: MetadataExtractionState) -> MetadataExtractionState:
    """Detect Phase 2: Business Planning documents."""
    results = call_llm_for_phase(
        state["content"],
        PHASE_2_BUSINESS_PLANNING,
        state["total_lines"]
    )
    state["phase2_results"] = results
    return state


def detect_phase3_documents(state: MetadataExtractionState) -> MetadataExtractionState:
    """Detect Phase 3: Feasibility & Risk Analysis documents."""
    results = call_llm_for_phase(
        state["content"],
        PHASE_3_FEASIBILITY_RISK,
        state["total_lines"]
    )
    state["phase3_results"] = results
    return state


def detect_phase4_documents(state: MetadataExtractionState) -> MetadataExtractionState:
    """Detect Phase 4: High-Level Design documents."""
    results = call_llm_for_phase(
        state["content"],
        PHASE_4_HIGH_LEVEL_DESIGN,
        state["total_lines"]
    )
    state["phase4_results"] = results
    return state


def detect_phase5_documents(state: MetadataExtractionState) -> MetadataExtractionState:
    """Detect Phase 5: Low-Level Design documents."""
    results = call_llm_for_phase(
        state["content"],
        PHASE_5_LOW_LEVEL_DESIGN,
        state["total_lines"]
    )
    state["phase5_results"] = results
    return state


def detect_phase6_documents(state: MetadataExtractionState) -> MetadataExtractionState:
    """Detect Phase 6: UI/UX Design documents."""
    results = call_llm_for_phase(
        state["content"],
        PHASE_6_UIUX_DESIGN,
        state["total_lines"]
    )
    state["phase6_results"] = results
    return state


def detect_phase7_documents(state: MetadataExtractionState) -> MetadataExtractionState:
    """Detect Phase 7: Testing & QA documents."""
    results = call_llm_for_phase(
        state["content"],
        PHASE_7_TESTING_QA,
        state["total_lines"]
    )
    state["phase7_results"] = results
    return state


def detect_additional_documents(state: MetadataExtractionState) -> MetadataExtractionState:
    """Detect additional document types (SRS, Diagrams)."""
    results = call_llm_for_phase(
        state["content"],
        ADDITIONAL_DOCUMENT_TYPES,
        state["total_lines"]
    )
    state["additional_results"] = results
    return state


def aggregate_results(state: MetadataExtractionState) -> MetadataExtractionState:
    """Aggregate all phase results into final response."""
    all_results = []
    
    # Collect results from all phases
    for phase_key in [
        "phase1_results", "phase2_results", "phase3_results",
        "phase4_results", "phase5_results", "phase6_results",
        "phase7_results", "additional_results"
    ]:
        phase_results = state.get(phase_key, [])
        if phase_results:
            all_results.extend(phase_results)
    
    # Build response object
    response_items = []
    seen_types = set()
    
    for result in all_results:
        doc_type = result.get("type", "")
        if doc_type and doc_type not in seen_types:
            seen_types.add(doc_type)
            response_items.append({
                "type": doc_type,
                "line_start": result.get("line_start", -1),
                "line_end": result.get("line_end", -1)
            })
    
    # Ensure all document types are present
    for dt in ALL_DOCUMENT_TYPES:
        if dt not in seen_types:
            response_items.append({
                "type": dt,
                "line_start": -1,
                "line_end": -1
            })
    
    state["response"] = {
        "document_id": state["document_id"],
        "type": "metadata_extraction",
        "response": response_items
    }
    
    return state


# ============================================================================
# Build Workflow Graph
# ============================================================================

def build_metadata_extraction_workflow() -> StateGraph:
    """Build the metadata extraction workflow graph."""
    workflow = StateGraph(MetadataExtractionState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_state)
    workflow.add_node("detect_phase1", detect_phase1_documents)
    workflow.add_node("detect_phase2", detect_phase2_documents)
    workflow.add_node("detect_phase3", detect_phase3_documents)
    workflow.add_node("detect_phase4", detect_phase4_documents)
    workflow.add_node("detect_phase5", detect_phase5_documents)
    workflow.add_node("detect_phase6", detect_phase6_documents)
    workflow.add_node("detect_phase7", detect_phase7_documents)
    workflow.add_node("detect_additional", detect_additional_documents)
    workflow.add_node("aggregate", aggregate_results)
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    # Define edges (sequential processing through phases)
    workflow.add_edge("initialize", "detect_phase1")
    workflow.add_edge("detect_phase1", "detect_phase2")
    workflow.add_edge("detect_phase2", "detect_phase3")
    workflow.add_edge("detect_phase3", "detect_phase4")
    workflow.add_edge("detect_phase4", "detect_phase5")
    workflow.add_edge("detect_phase5", "detect_phase6")
    workflow.add_edge("detect_phase6", "detect_phase7")
    workflow.add_edge("detect_phase7", "detect_additional")
    workflow.add_edge("detect_additional", "aggregate")
    workflow.add_edge("aggregate", END)
    
    return workflow


# Compile the workflow graph
metadata_extraction_graph = build_metadata_extraction_workflow().compile()


# ============================================================================
# Direct Invocation Helper
# ============================================================================

def extract_metadata(document_id: str, content: str, filename: Optional[str] = None) -> Dict:
    """
    Direct helper function to extract metadata from content.
    
    Args:
        document_id: UUID of the document
        content: Markdown content to analyze
        filename: Optional filename for context
        
    Returns:
        Metadata extraction response dict
    """
    state = {
        "document_id": document_id,
        "content": content,
        "filename": filename,
        "total_lines": 0,
        "phase1_results": None,
        "phase2_results": None,
        "phase3_results": None,
        "phase4_results": None,
        "phase5_results": None,
        "phase6_results": None,
        "phase7_results": None,
        "additional_results": None,
        "response": None,
    }
    
    result = metadata_extraction_graph.invoke(state)
    return result.get("response", {})
