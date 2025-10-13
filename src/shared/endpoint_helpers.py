"""
Helper functions for API endpoints.
"""

import logging
from typing import Dict, Any
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def parse_service_error(error: Exception, default_message: str = "Có lỗi xảy ra") -> Dict[str, Any]:
    """
    Parse error from service layer and return structured error response.

    Args:
        error: Exception from service layer
        default_message: Default user message if parsing fails

    Returns:
        Structured error dict
    """
    error_str = str(error)

    # Try to parse as dict string (AI-friendly format)
    try:
        if error_str.startswith("{") and "error_id" in error_str:
            # It's already a formatted error dict string, evaluate it
            error_dict = eval(error_str)
            return error_dict
    except Exception as parse_error:
        logger.warning(f"Failed to parse error as dict: {parse_error}")

    # Fallback to simple error response
    return {
        "user_message": f"⚠️ {default_message}",
        "technical_details": {
            "error_message": error_str
        },
        "suggestions": [
            "Thử lại sau vài phút",
            "Kiểm tra kết nối mạng",
            "Liên hệ admin nếu lỗi vẫn tiếp diễn"
        ]
    }


def raise_ai_friendly_http_exception(
    error: Exception,
    default_message: str = "Có lỗi xảy ra",
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> None:
    """
    Raise HTTPException with AI-friendly error details.

    Args:
        error: Original exception
        default_message: Default user message
        status_code: HTTP status code

    Raises:
        HTTPException with structured error details
    """
    error_detail = parse_service_error(error, default_message)
    logger.error(f"Raising HTTP {status_code}: {error_detail}")

    raise HTTPException(
        status_code=status_code,
        detail=error_detail
    )
