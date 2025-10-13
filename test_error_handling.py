"""
Test script to demonstrate AI-friendly error handling.

This script simulates different error scenarios to show how the
AI-friendly error messages are generated.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from shared.error_handler import (
    ValidationError,
    LLMServiceError,
    WorkflowError,
    DatabaseError,
    InternalError
)
import json


def print_error(title: str, error_dict: dict):
    """Pretty print error response."""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {title}")
    print(f"{'='*80}")
    print(json.dumps(error_dict, indent=2, ensure_ascii=False))
    print(f"{'='*80}\n")


def main():
    """Run error handling tests."""

    print("\n" + "🚀 " * 20)
    print("BA COPILOT AI - AI-FRIENDLY ERROR HANDLING DEMONSTRATION")
    print("🚀 " * 20 + "\n")

    # Test 1: Validation Error - Invalid Input
    print_error(
        "Validation Error - Invalid Project Input",
        ValidationError.invalid_input(
            "project_input",
            "Mô tả dự án phải có ít nhất 10 ký tự",
            "Test"
        )
    )

    # Test 2: Validation Error - Missing Required Field
    print_error(
        "Validation Error - Missing Required Field",
        ValidationError.missing_required_field("api_key")
    )

    # Test 3: LLM Service Error - Provider Unavailable
    print_error(
        "LLM Service Error - Provider Unavailable",
        LLMServiceError.provider_unavailable(
            "Google Gemini",
            Exception("Connection timeout: Unable to reach API server")
        )
    )

    # Test 4: LLM Service Error - Generation Failed
    print_error(
        "LLM Service Error - Generation Failed",
        LLMServiceError.generation_failed(
            "tài liệu SRS",
            Exception("Quota exceeded: You have exceeded your API quota limit")
        )
    )

    # Test 5: LLM Service Error - API Key Missing
    print_error(
        "LLM Service Error - API Key Missing",
        LLMServiceError.api_key_missing("Google Gemini")
    )

    # Test 6: Workflow Error - Initialization Failed
    print_error(
        "Workflow Error - Initialization Failed",
        WorkflowError.workflow_initialization_failed(
            "SRS Workflow",
            Exception("Failed to load workflow configuration: Config file not found")
        )
    )

    # Test 7: Workflow Error - Execution Failed
    print_error(
        "Workflow Error - Execution Failed",
        WorkflowError.workflow_execution_failed(
            "SRS Generation Workflow",
            "validate_requirements",
            Exception("Validation step failed: Requirements format invalid")
        )
    )

    # Test 8: Database Error - Connection Failed
    print_error(
        "Database Error - Connection Failed",
        DatabaseError.connection_failed(
            Exception("FATAL: password authentication failed for user 'bacopilot'")
        )
    )

    # Test 9: Database Error - Query Failed
    print_error(
        "Database Error - Query Failed",
        DatabaseError.query_failed(
            "INSERT INTO documents",
            Exception("IntegrityError: duplicate key value violates unique constraint")
        )
    )

    # Test 10: Internal Error - Unexpected Error
    print_error(
        "Internal Error - Unexpected Error",
        InternalError.unexpected_error(
            "tạo tài liệu SRS",
            Exception("AttributeError: 'NoneType' object has no attribute 'generate'")
        )
    )

    print("\n" + "✅ " * 20)
    print("ALL ERROR SCENARIOS DEMONSTRATED SUCCESSFULLY!")
    print("✅ " * 20 + "\n")

    # Example of how endpoint would use these errors
    print("\n" + "📚 " * 20)
    print("EXAMPLE: How Endpoint Uses AI-Friendly Errors")
    print("📚 " * 20 + "\n")

    print("""
Example code in endpoint:

```python
from shared.endpoint_helpers import raise_ai_friendly_http_exception

@router.post("/generate")
async def generate_srs_document(request: SRSGenerateRequest):
    try:
        # Validate input
        if not await srs_service.validate_input(request.project_input):
            error_response = ValidationError.invalid_input(
                "project_input",
                "Mô tả dự án phải có ít nhất 10 ký tự",
                request.project_input
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response
            )

        # Generate SRS
        result = await srs_service.generate_srs(...)
        return result

    except HTTPException:
        raise
    except Exception as e:
        # This will parse and return AI-friendly error
        raise_ai_friendly_http_exception(
            e,
            default_message="Không thể tạo tài liệu SRS"
        )
```

The client receives a structured JSON error response:

```json
{
  "error_id": "err_20251013_034500_123456",
  "category": "llm_service",
  "timestamp": "2025-10-13T03:45:00.123456",
  "user_message": "🤖 Dịch vụ AI (Google Gemini) tạm thời không khả dụng",
  "technical_details": {
    "error_type": "ConnectionError",
    "error_message": "Connection timeout: Unable to reach API server",
    "context": {
      "provider": "Google Gemini",
      "error_details": "..."
    }
  },
  "suggestions": [
    "Kiểm tra API key trong file .env",
    "Đảm bảo Google Gemini API có thể truy cập từ server",
    "Kiểm tra quota và giới hạn API",
    "Thử lại sau vài phút"
  ],
  "debug_info": {
    "file_location": "src/services/llm_service.py:28",
    "function_name": "_ensure_initialized"
  }
}
```
    """)

    print("\n" + "🎉 " * 20)
    print("DEMONSTRATION COMPLETE!")
    print("🎉 " * 20 + "\n")


if __name__ == "__main__":
    main()
