"""
Custom exceptions for Mermaid validation service.
"""

class MermaidValidatorError(Exception):
    """Base exception for Mermaid validator errors"""
    pass


class SubprocessStartupError(MermaidValidatorError):
    """Raised when Node.js subprocess fails to start"""
    pass


class SubprocessUnavailable(MermaidValidatorError):
    """Raised when subprocess is not running or unreachable"""
    pass


class ValidationTimeout(MermaidValidatorError):
    """Raised when validation request times out"""
    def __init__(self, message: str, timeout: float):
        super().__init__(message)
        self.timeout = timeout