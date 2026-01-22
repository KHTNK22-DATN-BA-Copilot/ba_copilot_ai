# workflows/nodes/get_content_file.py
"""
Module to fetch file content from Supabase Storage.
This replaces the OCR-based file processing with direct content retrieval from Supabase.
"""

import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "uploads")

# Import supabase client lazily to avoid import errors if not configured
_supabase_client = None


def get_supabase_client():
    """
    Get or create Supabase client instance (lazy initialization).

    Returns:
        Supabase client instance
    """
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables. "
                "Please check your .env file."
            )
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


async def list_file_from_supabase(storage_paths: List[str]) -> List[Dict[str, str]]:
    """
    Download files from Supabase Storage and extract content.
    Logic follows the pattern from backend service.

    Args:
        storage_paths: List of file paths in Supabase Storage

    Returns:
        List of dictionaries containing filename and content
    """
    file_contents = []
    supabase = get_supabase_client()

    for file_path in storage_paths:
        if not file_path:
            continue

        try:
            file_bytes = supabase.storage.from_(SUPABASE_BUCKET).download(file_path)

            # Decode bytes to UTF-8 text, ignoring errors
            content = file_bytes.decode("utf-8", errors="ignore")

            file_contents.append({
                "filename": file_path.split("/")[-1],
                "content": content
            })

        except Exception as e:
            print(f"Error when getting file '{file_path}': {e}")

    return file_contents


def get_content_from_storage(storage_paths: List[str]) -> str:
    """
    Download files from Supabase Storage and combine text content.

    Args:
        storage_paths: List of file paths in Supabase Storage

    Returns:
        Combined text content from all files
    """
    if not storage_paths:
        return ""

    # Run async function synchronously
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    file_contents = loop.run_until_complete(list_file_from_supabase(storage_paths))

    # Combine all file contents
    extracted_texts = []
    for file_info in file_contents:
        filename = file_info.get("filename", "unknown")
        content = file_info.get("content", "")

        if content:
            extracted_texts.append(f"### File: {filename}\n{content}\n")

    combined_text = "\n".join(extracted_texts) if extracted_texts else ""
    print(f"Supabase content processed: {len(file_contents)} files, {len(combined_text)} characters")

    return combined_text


def get_content_file(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function to fetch and process files from Supabase Storage.
    This function replaces process_ocr for Supabase-based file retrieval.

    Args:
        state: Current workflow state containing storage_paths, expect it to have the name "storage_paths",
          i.e. `state.get("storage_paths", [])`

    Returns:
        ""(empty string) if `state.get("storage_paths", [])` is empty or None
        Updated state with extracted_text
    """
    storage_paths = state.get("storage_paths", [])

    if not storage_paths:
        print("No storage_paths provided, skipping file content retrieval")
        state["extracted_text"] = ""
        return state

    try:
        # Get content from Supabase storage
        extracted_text = get_content_from_storage(storage_paths)
        state["extracted_text"] = extracted_text

    except Exception as e:
        print(f"Error fetching content from Supabase: {e}")
        state["extracted_text"] = ""

    return state
