# Error Handling Guide

## Overview

BA Copilot AI sử dụng hệ thống AI-friendly error handling để cung cấp:
- 🎯 **User-friendly messages** (tiếng Việt)
- 🔧 **Technical details** cho developers
- 📊 **Error tracking** với unique error IDs
- 💡 **Actionable suggestions** để khắc phục

## Error Response Format

Mọi error response đều có cấu trúc:

```json
{
  "error_id": "err_YYYYMMDD_HHMMSS_microseconds",
  "category": "validation|llm_service|workflow|database|internal",
  "timestamp": "ISO 8601 timestamp",
  "user_message": "🎯 Thông báo thân thiện cho user",
  "technical_details": {
    "error_type": "Exception class name",
    "error_message": "Original error message",
    "context": {
      "key": "value pairs with relevant context"
    }
  },
  "suggestions": [
    "Gợi ý 1",
    "Gợi ý 2"
  ],
  "debug_info": {
    "file_location": "src/path/to/file.py:line_number",
    "function_name": "function_name"
  }
}
```

## Error Categories

### 1. Validation Errors (`validation`)
**HTTP Status**: 400 Bad Request

Lỗi khi dữ liệu đầu vào không hợp lệ.

**Example**:
```python
from shared.error_handler import ValidationError

error_response = ValidationError.invalid_input(
    "project_input",
    "Mô tả dự án phải có ít nhất 10 ký tự",
    user_input
)
```

### 2. LLM Service Errors (`llm_service`)
**HTTP Status**: 500 Internal Server Error

Lỗi liên quan đến AI/LLM services (Google Gemini, OpenAI, etc.)

**Common Scenarios**:
- Provider unavailable
- API key missing
- Quota exceeded
- Generation failed

**Example**:
```python
from shared.error_handler import LLMServiceError

error_response = LLMServiceError.provider_unavailable(
    "Google Gemini",
    original_exception
)
```

### 3. Workflow Errors (`workflow`)
**HTTP Status**: 500 Internal Server Error

Lỗi trong quá trình xử lý workflow (LangGraph)

**Example**:
```python
from shared.error_handler import WorkflowError

error_response = WorkflowError.workflow_execution_failed(
    "SRS Generation Workflow",
    "validate_requirements",
    original_exception
)
```

### 4. Database Errors (`database`)
**HTTP Status**: 500 Internal Server Error

Lỗi khi tương tác với database

**Example**:
```python
from shared.error_handler import DatabaseError

error_response = DatabaseError.connection_failed(original_exception)
```

### 5. Internal Errors (`internal`)
**HTTP Status**: 500 Internal Server Error

Lỗi không xác định hoặc unexpected

**Example**:
```python
from shared.error_handler import InternalError

error_response = InternalError.unexpected_error(
    "tạo tài liệu SRS",
    original_exception
)
```

## Usage in Code

### In Services

```python
from shared.error_handler import LLMServiceError, InternalError

async def generate_srs(project_input: str) -> Dict[str, Any]:
    try:
        # Get LLM service
        try:
            llm_service = get_llm_service()
        except Exception as e:
            error_response = LLMServiceError.provider_unavailable("LLM Service", e)
            raise Exception(str(error_response))

        # Generate content
        try:
            content = await llm_service.generate_srs_document(project_input)
        except Exception as e:
            error_response = LLMServiceError.generation_failed("tài liệu SRS", e)
            raise Exception(str(error_response))

        return content

    except Exception as e:
        # Check if already formatted
        if "error_id" in str(e):
            raise
        else:
            error_response = InternalError.unexpected_error("tạo tài liệu SRS", e)
            raise Exception(str(error_response))
```

### In Endpoints

```python
from shared.error_handler import ValidationError
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

        # Call service
        result = await srs_service.generate_srs(request.project_input)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise_ai_friendly_http_exception(
            e,
            default_message="Không thể tạo tài liệu SRS"
        )
```

## Testing Errors

### Run Test Script
```bash
python3 test_error_handling.py
```

### Test with cURL

**Validation Error**:
```bash
curl -X POST "http://localhost:8000/v1/srs/generate" \
  -H "Content-Type: application/json" \
  -d '{"project_input": "abc"}'
```

**Expected Response**:
```json
{
  "error_id": "err_...",
  "category": "validation",
  "user_message": "❌ Dữ liệu đầu vào không hợp lệ: project_input",
  "technical_details": {...},
  "suggestions": [...]
}
```

## Logging

Errors are automatically logged with full details:

```
[err_20251013_034500_123456] LLM_SERVICE ERROR: 🤖 Dịch vụ AI tạm thời không khả dụng
Type: ConnectionError
Message: Connection timeout
Context: {'provider': 'Google Gemini'}
Stack Trace:
  File "src/services/llm_service.py", line 28, in _ensure_initialized
    ...
```

## Best Practices

### ✅ DO

- Use appropriate error category
- Provide helpful user messages in Vietnamese
- Include relevant context in technical_details
- Add actionable suggestions
- Let the error handler extract stack trace

### ❌ DON'T

- Don't hardcode error messages
- Don't expose sensitive information in user messages
- Don't swallow exceptions silently
- Don't create generic "Something went wrong" messages
- Don't forget to re-raise formatted errors

## Error Tracking

### For Users
- Báo lỗi với **error_id** cho support team
- Follow **suggestions** để tự khắc phục

### For Developers
- Search logs với **error_id**
- Check **file_location** và **function_name**
- Review **context** để understand root cause
- Monitor **category** distribution để identify patterns

## Extending Error Handling

### Add New Error Type

1. **Create error class in error_handler.py**:
```python
class PaymentError:
    """Payment error handler."""

    @staticmethod
    def payment_failed(amount: float, original_error: Exception) -> Dict[str, Any]:
        return AIFriendlyError.create_error_response(
            error=original_error,
            category=ErrorCategory.EXTERNAL_API,
            user_message=f"💳 Thanh toán ${amount} thất bại",
            technical_context={
                "amount": amount,
                "error_details": str(original_error)
            },
            suggestions=[
                "Kiểm tra thông tin thẻ",
                "Đảm bảo số dư đủ",
                "Liên hệ ngân hàng nếu vấn đề vẫn tiếp diễn"
            ]
        )
```

2. **Use in service**:
```python
from shared.error_handler import PaymentError

try:
    process_payment(amount)
except Exception as e:
    error_response = PaymentError.payment_failed(amount, e)
    raise Exception(str(error_response))
```

## FAQ

**Q: Tại sao sử dụng tiếng Việt cho user_message?**
A: Để user dễ hiểu. Technical details vẫn giữ tiếng Anh cho developers.

**Q: Error ID có unique không?**
A: Có, format: `err_YYYYMMDD_HHMMSS_microseconds`

**Q: Có thể disable debug_info trong production không?**
A: Có, modify `AIFriendlyError.create_error_response()` để check environment.

**Q: Làm sao track errors trong production?**
A: Search logs với error_id hoặc integrate với error tracking service (Sentry, etc.)

## Related Files

- **Implementation**: `src/shared/error_handler.py`
- **Helpers**: `src/shared/endpoint_helpers.py`
- **Tests**: `test_error_handling.py`
- **Summary**: `IMPLEMENTATION_SUMMARY.md`
