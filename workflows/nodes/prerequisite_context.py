# workflows/nodes/prerequisite_context.py
"""
Prerequisite Context Handler

This module provides utilities for handling prerequisite document context
in AI workflows. It enhances the existing get_content_file functionality
by providing structured context formatting for better AI generation.

The Backend service is responsible for:
- Validating document constraints and prerequisites
- Filtering and providing only required prerequisite documents via storage_paths

The AI service (this module) is responsible for:
- Loading prerequisite documents from storage
- Formatting context in a clear, structured way for AI prompts
- Incorporating prerequisite context into generation prompts
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


def format_prerequisite_context(
    extracted_text: str,
    chat_context: Optional[str] = None,
    user_message: Optional[str] = None
) -> str:
    """
    Format prerequisite document context for AI prompt inclusion.
    
    Args:
        extracted_text: Combined content from prerequisite documents (from storage_paths)
        chat_context: Optional conversation history context
        user_message: Optional user's generation request
        
    Returns:
        Formatted context string ready for AI prompt inclusion
    """
    context_parts = []
    
    # Add prerequisite documents if available
    if extracted_text and extracted_text.strip():
        context_parts.append(
            "### PREREQUISITE DOCUMENTS\n"
            "The following prerequisite documents have been validated and provided as context.\n"
            "Use this information to ensure consistency and completeness in your response.\n\n"
            f"{extracted_text}\n"
        )
    
    # Add chat history if available
    if chat_context and chat_context.strip():
        context_parts.append(
            "### CONVERSATION HISTORY\n"
            "Previous conversation context for continuity:\n\n"
            f"{chat_context}\n"
        )
    
    # Combine all context
    if context_parts:
        formatted_context = "\n".join(context_parts)
        logger.info(
            f"Formatted prerequisite context: "
            f"{len(extracted_text) if extracted_text else 0} chars from prerequisites, "
            f"{len(chat_context) if chat_context else 0} chars from chat history"
        )
        return formatted_context
    
    return ""


def build_context_aware_prompt(
    base_prompt: str,
    extracted_text: Optional[str] = None,
    chat_context: Optional[str] = None,
    context_position: str = "top"
) -> str:
    """
    Build a context-aware prompt by combining base prompt with prerequisite context.
    
    Args:
        base_prompt: The base generation prompt template
        extracted_text: Content from prerequisite documents
        chat_context: Conversation history
        context_position: Where to place context ("top" or "bottom")
        
    Returns:
        Complete prompt with context integrated
    """
    prerequisite_context = format_prerequisite_context(
        extracted_text=extracted_text or "",
        chat_context=chat_context
    )
    
    if not prerequisite_context:
        # No context available, return base prompt as-is
        return base_prompt
    
    # Add context at specified position
    if context_position == "top":
        return f"{prerequisite_context}\n\n{base_prompt}"
    else:
        return f"{base_prompt}\n\n{prerequisite_context}"


def log_prerequisite_usage(state: Dict[str, Any], workflow_name: str) -> None:
    """
    Log information about prerequisite document usage for debugging and monitoring.
    
    Args:
        state: Workflow state dictionary
        workflow_name: Name of the current workflow
    """
    storage_paths = state.get('storage_paths', [])
    extracted_text = state.get('extracted_text', '')
    
    if storage_paths:
        logger.info(
            f"[{workflow_name}] Using {len(storage_paths)} prerequisite document(s): "
            f"{', '.join([path.split('/')[-1] for path in storage_paths])}"
        )
    else:
        logger.info(f"[{workflow_name}] No prerequisite documents provided")
    
    if extracted_text:
        logger.info(
            f"[{workflow_name}] Extracted text length: {len(extracted_text)} characters"
        )


def validate_prerequisite_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that prerequisite context is properly loaded in workflow state.
    This helps catch issues where storage_paths were provided but content wasn't fetched.
    
    Args:
        state: Workflow state dictionary
        
    Returns:
        State dictionary (unchanged, but logged for debugging)
    """
    storage_paths = state.get('storage_paths', [])
    extracted_text = state.get('extracted_text', '')
    
    if storage_paths and not extracted_text:
        logger.warning(
            f"Prerequisite validation warning: storage_paths provided ({len(storage_paths)} files) "
            "but extracted_text is empty. Ensure get_content_file node was executed."
        )
    
    if extracted_text and not storage_paths:
        logger.info(
            "Note: extracted_text present without storage_paths. "
            "This may be from manual context or previous state."
        )
    
    return state


# Convenience functions for common context patterns

def get_prerequisite_summary(extracted_text: str, max_length: int = 500) -> str:
    """
    Get a summary of prerequisite content for logging/debugging.
    
    Args:
        extracted_text: Full prerequisite text
        max_length: Maximum length for summary
        
    Returns:
        Truncated summary with ellipsis if needed
    """
    if not extracted_text:
        return "No prerequisite content"
    
    text = extracted_text.strip()
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "... (truncated)"


def count_prerequisite_documents(extracted_text: str) -> int:
    """
    Count the number of prerequisite documents in extracted text.
    Assumes files are separated by "### File:" markers (from get_content_file).
    
    Args:
        extracted_text: Combined prerequisite text
        
    Returns:
        Number of documents found
    """
    if not extracted_text:
        return 0
    
    return extracted_text.count("### File:")


def extract_prerequisite_filenames(extracted_text: str) -> List[str]:
    """
    Extract filenames from prerequisite document text.
    Parses "### File: filename" markers added by get_content_file.
    
    Args:
        extracted_text: Combined prerequisite text
        
    Returns:
        List of filenames found
    """
    if not extracted_text:
        return []
    
    filenames = []
    for line in extracted_text.split('\n'):
        if line.startswith("### File:"):
            filename = line.replace("### File:", "").strip()
            if filename:
                filenames.append(filename)
    
    return filenames
