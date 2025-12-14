# workflows/nodes/node_ocr.py
import os
import io
import base64
from typing import TypedDict, List, Dict, Any, Optional
from fastapi import UploadFile
import PyPDF2
from PIL import Image
import pytesseract
from docx import Document

# Supported file types
SUPPORTED_IMAGE_TYPES = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
SUPPORTED_DOC_TYPES = ['.pdf', '.docx', '.txt']


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from image using OCR (Tesseract)

    Args:
        image_bytes: Image file bytes

    Returns:
        Extracted text
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF file

    Args:
        pdf_bytes: PDF file bytes

    Returns:
        Extracted text
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


def extract_text_from_docx(docx_bytes: bytes) -> str:
    """
    Extract text from DOCX file

    Args:
        docx_bytes: DOCX file bytes

    Returns:
        Extracted text
    """
    try:
        doc = Document(io.BytesIO(docx_bytes))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""


def extract_text_from_txt(txt_bytes: bytes) -> str:
    """
    Extract text from TXT file

    Args:
        txt_bytes: TXT file bytes

    Returns:
        Extracted text
    """
    try:
        text = txt_bytes.decode('utf-8')
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from TXT: {e}")
        return ""


def process_file(file_bytes: bytes, filename: str) -> str:
    """
    Process file and extract text based on file type

    Args:
        file_bytes: File bytes
        filename: Original filename

    Returns:
        Extracted text
    """
    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext in SUPPORTED_IMAGE_TYPES:
        return extract_text_from_image(file_bytes)
    elif file_ext == '.pdf':
        return extract_text_from_pdf(file_bytes)
    elif file_ext == '.docx':
        return extract_text_from_docx(file_bytes)
    elif file_ext == '.txt':
        return extract_text_from_txt(file_bytes)
    else:
        print(f"Unsupported file type: {file_ext}")
        return ""


def process_ocr(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node function to process OCR from uploaded files

    Args:
        state: Current workflow state containing files or file_data

    Returns:
        Updated state with extracted_text
    """
    extracted_texts = []

    # Check if files are provided in state
    files = state.get("files", [])
    file_data = state.get("file_data", [])

    # Process files from UploadFile objects
    if files:
        for file in files:
            try:
                if hasattr(file, 'read'):
                    # If it's an UploadFile or file-like object
                    file_bytes = file.read()
                    if hasattr(file, 'filename'):
                        filename = file.filename
                    else:
                        filename = "unknown"

                    text = process_file(file_bytes, filename)
                    if text:
                        extracted_texts.append(f"### File: {filename}\n{text}\n")

                    # Reset file pointer if possible
                    if hasattr(file, 'seek'):
                        file.seek(0)
            except Exception as e:
                print(f"Error processing file: {e}")

    # Process files from file_data (dict with filename and bytes)
    if file_data:
        for file_info in file_data:
            try:
                filename = file_info.get("filename", "unknown")
                file_bytes = file_info.get("bytes", b"")

                if file_bytes:
                    text = process_file(file_bytes, filename)
                    if text:
                        extracted_texts.append(f"### File: {filename}\n{text}\n")
            except Exception as e:
                print(f"Error processing file data: {e}")

    # Combine all extracted text
    combined_text = "\n".join(extracted_texts) if extracted_texts else ""

    state["extracted_text"] = combined_text

    print(f"OCR processed: {len(extracted_texts)} files, {len(combined_text)} characters")

    return state


def process_ocr_sync(files: List[UploadFile]) -> str:
    """
    Synchronous function to process OCR from uploaded files (for FastAPI endpoints)

    Args:
        files: List of UploadFile objects

    Returns:
        Combined extracted text
    """
    state = {"files": files}
    result_state = process_ocr(state)
    return result_state.get("extracted_text", "")
