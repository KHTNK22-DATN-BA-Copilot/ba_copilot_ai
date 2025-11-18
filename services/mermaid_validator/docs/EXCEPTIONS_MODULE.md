# Mermaid Validation - Missing Exceptions Module

## 🎯 Objective

Create the missing `exceptions.py` module that was referenced throughout the implementation but not yet created.

---

## 🛠️ Implementation

**File**: `services/mermaid_validator/exceptions.py`

```python
"""
Custom exceptions for Mermaid validator service.

Exception Hierarchy:
    MermaidValidatorError (base)
    ├── SubprocessStartupError
    ├── SubprocessUnavailable
    └── ValidationTimeout
"""


class MermaidValidatorError(Exception):
    """
    Base exception for all Mermaid validator errors.

    All custom exceptions in this module inherit from this base class,
    making it easy to catch any validator-related error.

    Example:
        try:
            await validator.validate(code)
        except MermaidValidatorError as e:
            logger.error(f"Validation error: {e}")
    """
    pass


class SubprocessStartupError(MermaidValidatorError):
    """
    Raised when Node.js validator subprocess fails to start.

    This typically indicates:
        - Node.js not installed
        - Script path incorrect
        - Port already in use
        - Timeout waiting for health check

    Example:
        raise SubprocessStartupError("Failed to start subprocess: timeout after 30s")
    """
    pass


class SubprocessUnavailable(MermaidValidatorError):
    """
    Raised when validator subprocess is not reachable.

    This can occur when:
        - Subprocess has crashed
        - HTTP connection fails
        - Subprocess not yet started
        - Network issues (firewall, etc.)

    Example:
        raise SubprocessUnavailable("Cannot connect to validator at http://localhost:3001")
    """
    pass


class ValidationTimeout(MermaidValidatorError):
    """
    Raised when validation request exceeds timeout.

    This indicates:
        - Complex diagram taking too long
        - Subprocess is hanging
        - Network latency issues

    Attributes:
        timeout: The timeout value (in seconds) that was exceeded

    Example:
        raise ValidationTimeout("Validation timeout", timeout=10)
    """

    def __init__(self, message: str, timeout: int = None):
        """
        Initialize timeout exception.

        Args:
            message: Error message
            timeout: Timeout value in seconds
        """
        super().__init__(message)
        self.timeout = timeout

    def __str__(self):
        """String representation with timeout info"""
        if self.timeout:
            return f"{super().__str__()} (timeout: {self.timeout}s)"
        return super().__str__()
```

---

## ✅ Verification

```powershell
# Test import
python -c "from services.mermaid_validator.exceptions import *; print('✓ Exceptions module OK')"
```

---

## 📝 Commit

```powershell
cd d:\Do_an_tot_nghiep\ba_copilot_ai

git add services/mermaid_validator/exceptions.py

git commit -m "feat: add custom exceptions for validator service

- Create MermaidValidatorError base exception
- Add SubprocessStartupError for startup failures
- Add SubprocessUnavailable for connection errors
- Add ValidationTimeout with timeout tracking

Exception Hierarchy:
  - MermaidValidatorError (base)
    - SubprocessStartupError
    - SubprocessUnavailable
    - ValidationTimeout

Refs: #OPS-317"
```

---

**Module Complete** ✅
