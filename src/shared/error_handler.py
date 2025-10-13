"""
AI-friendly error handler module.

Provides centralized error handling with user-friendly and debug-friendly error messages.
"""

import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorCategory(str, Enum):
    """Error categories for better classification."""
    VALIDATION = "validation"
    LLM_SERVICE = "llm_service"
    WORKFLOW = "workflow"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    AUTHENTICATION = "authentication"
    INTERNAL = "internal"


class AIFriendlyError:
    """
    AI-friendly error wrapper that provides detailed error information
    for debugging while maintaining user-friendly messages.
    """

    @staticmethod
    def create_error_response(
        error: Exception,
        category: ErrorCategory,
        user_message: str,
        technical_context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive error response.

        Args:
            error: The original exception
            category: Error category for classification
            user_message: User-friendly error message
            technical_context: Technical details for debugging
            suggestions: List of suggestions to fix the issue

        Returns:
            Dict containing error information
        """
        error_id = f"err_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        error_type = type(error).__name__
        error_message = str(error)

        # Get stack trace for debugging
        stack_trace = traceback.format_exc()

        # Log detailed error for server-side debugging
        logger.error(
            f"[{error_id}] {category.value.upper()} ERROR: {user_message}\n"
            f"Type: {error_type}\n"
            f"Message: {error_message}\n"
            f"Context: {technical_context}\n"
            f"Stack Trace:\n{stack_trace}"
        )

        # Build error response
        error_response = {
            "error_id": error_id,
            "category": category.value,
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "technical_details": {
                "error_type": error_type,
                "error_message": error_message,
                "context": technical_context or {}
            }
        }

        # Add suggestions if provided
        if suggestions:
            error_response["suggestions"] = suggestions

        # Add debug info in development mode
        # In production, you might want to remove or redact this
        error_response["debug_info"] = {
            "file_location": AIFriendlyError._extract_file_location(stack_trace),
            "function_name": AIFriendlyError._extract_function_name(stack_trace)
        }

        return error_response

    @staticmethod
    def _extract_file_location(stack_trace: str) -> str:
        """Extract file location from stack trace."""
        try:
            lines = stack_trace.split('\n')
            for line in reversed(lines):
                if 'File "' in line and 'src/' in line:
                    # Extract file path and line number
                    file_info = line.split('File "')[1].split('"')[0]
                    if ', line ' in line:
                        line_num = line.split(', line ')[1].split(',')[0].strip()
                        return f"{file_info}:{line_num}"
            return "unknown"
        except Exception:
            return "unknown"

    @staticmethod
    def _extract_function_name(stack_trace: str) -> str:
        """Extract function name from stack trace."""
        try:
            lines = stack_trace.split('\n')
            for line in reversed(lines):
                if ', in ' in line and 'src/' in line:
                    func_name = line.split(', in ')[1].strip()
                    return func_name
            return "unknown"
        except Exception:
            return "unknown"


class ValidationError:
    """Validation error handler."""

    @staticmethod
    def invalid_input(field_name: str, reason: str, value: Any = None) -> Dict[str, Any]:
        """Handle invalid input validation error."""
        return AIFriendlyError.create_error_response(
            error=ValueError(f"Invalid {field_name}: {reason}"),
            category=ErrorCategory.VALIDATION,
            user_message=f"❌ Dữ liệu đầu vào không hợp lệ: {field_name}",
            technical_context={
                "field": field_name,
                "reason": reason,
                "provided_value": str(value) if value else "empty"
            },
            suggestions=[
                f"Kiểm tra lại giá trị của trường '{field_name}'",
                f"Lý do: {reason}",
                "Đảm bảo dữ liệu đầu vào đáp ứng các yêu cầu"
            ]
        )

    @staticmethod
    def missing_required_field(field_name: str) -> Dict[str, Any]:
        """Handle missing required field error."""
        return AIFriendlyError.create_error_response(
            error=ValueError(f"Missing required field: {field_name}"),
            category=ErrorCategory.VALIDATION,
            user_message=f"❌ Thiếu trường bắt buộc: {field_name}",
            technical_context={
                "field": field_name,
                "requirement": "required"
            },
            suggestions=[
                f"Vui lòng cung cấp giá trị cho trường '{field_name}'",
                "Trường này là bắt buộc để xử lý yêu cầu"
            ]
        )


class LLMServiceError:
    """LLM service error handler."""

    @staticmethod
    def provider_unavailable(provider: str, original_error: Exception) -> Dict[str, Any]:
        """Handle LLM provider unavailable error."""
        return AIFriendlyError.create_error_response(
            error=original_error,
            category=ErrorCategory.LLM_SERVICE,
            user_message=f"🤖 Dịch vụ AI ({provider}) tạm thời không khả dụng",
            technical_context={
                "provider": provider,
                "error_details": str(original_error)
            },
            suggestions=[
                "Kiểm tra API key trong file .env",
                f"Đảm bảo {provider} API có thể truy cập từ server",
                "Kiểm tra quota và giới hạn API",
                "Thử lại sau vài phút"
            ]
        )

    @staticmethod
    def generation_failed(task: str, original_error: Exception) -> Dict[str, Any]:
        """Handle AI generation failed error."""
        return AIFriendlyError.create_error_response(
            error=original_error,
            category=ErrorCategory.LLM_SERVICE,
            user_message=f"🤖 Không thể tạo {task} bằng AI",
            technical_context={
                "task": task,
                "error_details": str(original_error)
            },
            suggestions=[
                "Thử lại với mô tả đầu vào rõ ràng hơn",
                "Kiểm tra kết nối mạng",
                "Đảm bảo dịch vụ AI đang hoạt động bình thường"
            ]
        )

    @staticmethod
    def api_key_missing(provider: str) -> Dict[str, Any]:
        """Handle missing API key error."""
        return AIFriendlyError.create_error_response(
            error=ValueError(f"Missing API key for {provider}"),
            category=ErrorCategory.LLM_SERVICE,
            user_message=f"🔑 Thiếu API key cho dịch vụ AI ({provider})",
            technical_context={
                "provider": provider,
                "config_issue": "api_key_not_configured"
            },
            suggestions=[
                f"Thêm {provider.upper()}_API_KEY vào file .env",
                "Sao chép từ .env.template và điền API key",
                "Restart server sau khi cập nhật .env"
            ]
        )


class WorkflowError:
    """Workflow error handler."""

    @staticmethod
    def workflow_initialization_failed(workflow_name: str, original_error: Exception) -> Dict[str, Any]:
        """Handle workflow initialization error."""
        return AIFriendlyError.create_error_response(
            error=original_error,
            category=ErrorCategory.WORKFLOW,
            user_message=f"⚙️ Không thể khởi tạo quy trình xử lý ({workflow_name})",
            technical_context={
                "workflow": workflow_name,
                "error_details": str(original_error)
            },
            suggestions=[
                "Kiểm tra cấu hình workflow trong code",
                "Đảm bảo tất cả dependencies được cài đặt",
                "Kiểm tra logs để xem lỗi chi tiết"
            ]
        )

    @staticmethod
    def workflow_execution_failed(workflow_name: str, step: str, original_error: Exception) -> Dict[str, Any]:
        """Handle workflow execution error."""
        return AIFriendlyError.create_error_response(
            error=original_error,
            category=ErrorCategory.WORKFLOW,
            user_message=f"⚙️ Lỗi trong quá trình xử lý tại bước: {step}",
            technical_context={
                "workflow": workflow_name,
                "failed_step": step,
                "error_details": str(original_error)
            },
            suggestions=[
                f"Kiểm tra logic xử lý tại bước '{step}'",
                "Review input data cho bước này",
                "Kiểm tra logs server để debug"
            ]
        )


class DatabaseError:
    """Database error handler."""

    @staticmethod
    def connection_failed(original_error: Exception) -> Dict[str, Any]:
        """Handle database connection error."""
        return AIFriendlyError.create_error_response(
            error=original_error,
            category=ErrorCategory.DATABASE,
            user_message="🗄️ Không thể kết nối đến cơ sở dữ liệu",
            technical_context={
                "error_details": str(original_error)
            },
            suggestions=[
                "Kiểm tra DATABASE_URL trong .env",
                "Đảm bảo PostgreSQL đang chạy",
                "Kiểm tra credentials (username/password)",
                "Verify network connectivity đến database server"
            ]
        )

    @staticmethod
    def query_failed(query_type: str, original_error: Exception) -> Dict[str, Any]:
        """Handle database query error."""
        return AIFriendlyError.create_error_response(
            error=original_error,
            category=ErrorCategory.DATABASE,
            user_message=f"🗄️ Lỗi khi thực hiện truy vấn: {query_type}",
            technical_context={
                "query_type": query_type,
                "error_details": str(original_error)
            },
            suggestions=[
                "Kiểm tra schema database",
                "Verify data integrity",
                "Review query logic trong code"
            ]
        )


class InternalError:
    """Internal server error handler."""

    @staticmethod
    def unexpected_error(operation: str, original_error: Exception) -> Dict[str, Any]:
        """Handle unexpected internal error."""
        return AIFriendlyError.create_error_response(
            error=original_error,
            category=ErrorCategory.INTERNAL,
            user_message=f"⚠️ Lỗi hệ thống không mong đợi khi thực hiện: {operation}",
            technical_context={
                "operation": operation,
                "error_details": str(original_error)
            },
            suggestions=[
                "Thử lại sau vài phút",
                "Liên hệ admin nếu lỗi vẫn tiếp diễn",
                "Cung cấp error_id khi báo cáo lỗi"
            ]
        )
