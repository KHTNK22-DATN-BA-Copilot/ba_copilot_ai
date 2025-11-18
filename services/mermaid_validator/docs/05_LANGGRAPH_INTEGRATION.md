# Phase 5: LangGraph Integration

## 🎯 Objective

Integrate Mermaid validation into LangGraph workflows, add validation and retry nodes, implement intelligent error correction with LLM, and update all diagram generation endpoints.

**Estimated Time**: 60-90 minutes  
**Commit Messages**:

1. `feat: integrate Mermaid validation into class diagram workflow`
2. `feat: add retry logic for diagram error correction`

---

## 🏗️ Workflow Architecture

### Enhanced Workflow with Validation

```
┌────────────────────────────────────────────────────────────┐
│           Class Diagram Generation Workflow                 │
└────────────────────────────────────────────────────────────┘

        START
          │
          ▼
    ┌─────────────┐
    │  Generate   │ ← LLM generates Mermaid code
    │  Diagram    │
    └─────┬───────┘
          │
          ▼
    ┌─────────────┐
    │  Validate   │ ← Node.js subprocess validates
    │  Mermaid    │
    └─────┬───────┘
          │
          ▼
    ┌──────────────────┐
    │  Valid?          │
    └──────┬───────────┘
           │
     ┌─────┴─────┐
     │           │
    YES          NO
     │           │
     │           ▼
     │     ┌──────────────┐
     │     │ Retry Count  │
     │     │    < 3?      │
     │     └───┬─────┬────┘
     │         │     │
     │        YES    NO
     │         │     │
     │         ▼     │
     │    ┌─────────┴────┐
     │    │   Fix        │ ← LLM retries with error context
     │    │   Diagram    │
     │    └────┬─────────┘
     │         │
     │         │ retry_count++
     │         │
     │         └────────────┐
     │                      │
     ▼                      ▼
┌─────────────┐      ┌─────────────┐
│  Format     │      │  Format     │
│  Response   │      │  Response   │
│  (Valid)    │      │  (Invalid)  │
└─────┬───────┘      └─────┬───────┘
      │                     │
      └──────────┬──────────┘
                 │
                 ▼
               END
```

---

## 🔍 State Management

### Enhanced State Schema

```python
from typing import TypedDict, Optional, List, Dict, Any
from typing_extensions import Annotated


class ClassDiagramState(TypedDict):
    """
    Enhanced state for class diagram workflow with validation.

    Fields:
        user_input: Original user description
        diagram_code: Generated Mermaid code (raw from LLM)
        validated_diagram: Validated/fixed Mermaid code
        validation_result: Result from validator subprocess
        retry_count: Number of fix attempts
        errors: Validation errors for retry context
        metadata: Additional info (validation time, etc.)
    """
    # Input
    user_input: str

    # Generation
    diagram_code: Optional[str]

    # Validation
    validated_diagram: Optional[str]
    validation_result: Optional[Dict[str, Any]]
    validated: bool

    # Retry logic
    retry_count: int
    errors: Optional[List[Dict[str, Any]]]

    # Output
    metadata: Optional[Dict[str, Any]]

    # System
    app_context: Optional[Dict[str, Any]]
```

---

## 🛠️ Implementation Steps

### Step 1: Create Validation Node

**File**: `workflows/class_diagram_workflow/nodes/validation.py`

```python
"""
Validation node for Mermaid diagram validation.
"""

import logging
from typing import Dict, Any

from ..state import ClassDiagramState
from services.mermaid_validator.exceptions import (
    SubprocessUnavailable,
    ValidationTimeout
)

logger = logging.getLogger(__name__)


async def validate_diagram_node(state: ClassDiagramState) -> Dict[str, Any]:
    """
    Validate generated Mermaid diagram.

    Uses Node.js subprocess validator to check syntax.

    Args:
        state: Current workflow state with diagram_code

    Returns:
        Updated state with validation_result and validated flag

    Graceful Degradation:
        If validator unavailable, marks as valid with warning
        to allow workflow to continue
    """
    diagram_code = state.get("validated_diagram") or state.get("diagram_code", "")
    retry_count = state.get("retry_count", 0)

    if not diagram_code:
        logger.error("No diagram code to validate")
        return {
            **state,
            "validation_result": {
                "valid": False,
                "errors": [{"message": "No diagram code generated", "type": "EmptyCode"}]
            },
            "validated": False,
            "errors": [{"message": "No diagram code generated"}]
        }

    # Get validator from app context
    validator = state.get("app_context", {}).get("validator")

    if not validator:
        logger.warning("Validator not available, skipping validation")
        return {
            **state,
            "validation_result": {
                "valid": True,
                "warning": "Validation service unavailable",
                "code": diagram_code
            },
            "validated_diagram": diagram_code,
            "validated": False  # Mark as unvalidated
        }

    try:
        logger.info(f"Validating diagram (attempt {retry_count + 1})...")

        # Validate via subprocess
        result = await validator.validate(diagram_code)

        is_valid = result.get("valid", False)

        logger.info(f"Validation result: {'✓ Valid' if is_valid else '✗ Invalid'}")

        if not is_valid:
            errors = result.get("errors", [])
            logger.warning(f"Validation errors: {errors}")

        return {
            **state,
            "validation_result": result,
            "validated_diagram": diagram_code if is_valid else state.get("validated_diagram"),
            "validated": is_valid,
            "errors": result.get("errors") if not is_valid else None
        }

    except SubprocessUnavailable as e:
        logger.error(f"Validator subprocess unavailable: {e}")
        # Graceful degradation: continue without validation
        return {
            **state,
            "validation_result": {
                "valid": True,
                "warning": f"Validator unavailable: {str(e)}",
                "code": diagram_code
            },
            "validated_diagram": diagram_code,
            "validated": False
        }

    except ValidationTimeout as e:
        logger.error(f"Validation timeout: {e}")
        return {
            **state,
            "validation_result": {
                "valid": True,
                "warning": f"Validation timeout: {str(e)}",
                "code": diagram_code
            },
            "validated_diagram": diagram_code,
            "validated": False
        }

    except Exception as e:
        logger.error(f"Unexpected validation error: {e}", exc_info=True)
        # Graceful degradation
        return {
            **state,
            "validation_result": {
                "valid": True,
                "warning": f"Validation error: {str(e)}",
                "code": diagram_code
            },
            "validated_diagram": diagram_code,
            "validated": False
        }
```

---

### Step 2: Create Fix/Retry Node

**File**: `workflows/class_diagram_workflow/nodes/fix.py`

````python
"""
Fix node for correcting invalid Mermaid diagrams using LLM.
"""

import logging
from typing import Dict, Any
from openai import AsyncOpenAI
import os

from ..state import ClassDiagramState

logger = logging.getLogger(__name__)

# Initialize OpenAI client for OpenRouter
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


async def fix_diagram_node(state: ClassDiagramState) -> Dict[str, Any]:
    """
    Fix invalid Mermaid diagram using LLM.

    Provides error context to LLM for intelligent correction.

    Args:
        state: Current workflow state with validation errors

    Returns:
        Updated state with fixed diagram_code
    """
    user_input = state.get("user_input", "")
    invalid_code = state.get("diagram_code", "")
    errors = state.get("errors", [])
    retry_count = state.get("retry_count", 0)

    logger.info(f"Attempting to fix diagram (retry {retry_count + 1}/3)...")

    # Build error context
    error_messages = "\n".join([
        f"- Line {err.get('line', '?')}: {err.get('message', 'Unknown error')}"
        for err in errors
    ])

    # LLM prompt for fixing
    fix_prompt = f"""The following Mermaid class diagram has syntax errors:

```mermaid
{invalid_code}
````

Validation Errors:
{error_messages}

Original Requirement:
{user_input}

Please fix the Mermaid code to be syntactically correct while maintaining the original intent.

Rules:

1. Output ONLY the corrected Mermaid code wrapped in `mermaid` blocks
2. Do NOT include explanations or additional text
3. Ensure proper Mermaid classDiagram syntax
4. Fix all validation errors

Corrected Mermaid Code:"""

    try:
        # Call LLM via OpenRouter
        response = await openai_client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a Mermaid diagram syntax expert. Fix invalid diagrams."
                },
                {
                    "role": "user",
                    "content": fix_prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent fixes
            max_tokens=2000
        )

        fixed_code = response.choices[0].message.content.strip()

        # Extract code from markdown if wrapped
        if "```mermaid" in fixed_code:
            fixed_code = fixed_code.split("```mermaid")[1].split("```")[0].strip()
        elif "```" in fixed_code:
            fixed_code = fixed_code.split("```")[1].split("```")[0].strip()

        logger.info("✓ Diagram fix attempted")

        return {
            **state,
            "diagram_code": fixed_code,
            "retry_count": retry_count + 1
        }

    except Exception as e:
        logger.error(f"Failed to fix diagram: {e}", exc_info=True)

        # Return original code if fix fails
        return {
            **state,
            "retry_count": retry_count + 1,
            "errors": errors + [{"message": f"Fix failed: {str(e)}", "type": "FixError"}]
        }

````

---

### Step 3: Update Workflow Graph

**File**: `workflows/class_diagram_workflow/workflow.py`

```python
"""
Enhanced class diagram workflow with Mermaid validation.
"""

import logging
from langgraph.graph import StateGraph, END
from typing import Dict, Any

from .state import ClassDiagramState
from .nodes.generation import generate_class_diagram_node
from .nodes.validation import validate_diagram_node
from .nodes.fix import fix_diagram_node

logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 3


def should_retry_validation(state: ClassDiagramState) -> str:
    """
    Conditional edge to determine next step after validation.

    Decision Logic:
        - Valid diagram? → format_response (done)
        - Invalid & retry_count < MAX_RETRIES? → fix_diagram (retry)
        - Invalid & retry_count >= MAX_RETRIES? → format_response (give up)

    Args:
        state: Current workflow state

    Returns:
        Next node name: "fix_diagram" or "format_response"
    """
    is_valid = state.get("validated", False)
    retry_count = state.get("retry_count", 0)

    if is_valid:
        logger.info("✓ Diagram is valid, proceeding to response")
        return "format_response"

    if retry_count < MAX_RETRIES:
        logger.warning(f"✗ Diagram invalid, retry {retry_count + 1}/{MAX_RETRIES}")
        return "fix_diagram"

    logger.error(f"✗ Max retries ({MAX_RETRIES}) reached, giving up")
    return "format_response"


def format_response_node(state: ClassDiagramState) -> Dict[str, Any]:
    """
    Format final response with metadata.

    Args:
        state: Final workflow state

    Returns:
        Formatted response
    """
    diagram_code = state.get("validated_diagram") or state.get("diagram_code", "")
    validation_result = state.get("validation_result", {})
    retry_count = state.get("retry_count", 0)
    validated = state.get("validated", False)

    # Build metadata
    metadata = {
        "validated": validated,
        "retry_count": retry_count,
        "validation_status": "valid" if validated else "invalid",
    }

    # Add validation details
    if validation_result:
        metadata["validation"] = {
            "diagram_type": validation_result.get("diagram_type"),
            "duration_ms": validation_result.get("duration_ms"),
            "warning": validation_result.get("warning")
        }

        if not validated and validation_result.get("errors"):
            metadata["errors"] = validation_result["errors"]

    return {
        **state,
        "validated_diagram": diagram_code,
        "metadata": metadata
    }


# Build workflow graph
def create_class_diagram_workflow() -> StateGraph:
    """
    Create class diagram workflow with validation and retry logic.

    Workflow:
        1. generate_class_diagram → Generate Mermaid code with LLM
        2. validate_diagram → Validate syntax with Node.js subprocess
        3. Conditional:
           - Valid? → format_response → END
           - Invalid & retries left? → fix_diagram → validate_diagram (loop)
           - Invalid & max retries? → format_response → END

    Returns:
        Configured StateGraph
    """
    workflow = StateGraph(ClassDiagramState)

    # Add nodes
    workflow.add_node("generate_class_diagram", generate_class_diagram_node)
    workflow.add_node("validate_diagram", validate_diagram_node)
    workflow.add_node("fix_diagram", fix_diagram_node)
    workflow.add_node("format_response", format_response_node)

    # Set entry point
    workflow.set_entry_point("generate_class_diagram")

    # Add edges
    workflow.add_edge("generate_class_diagram", "validate_diagram")
    workflow.add_edge("fix_diagram", "validate_diagram")  # Retry loop
    workflow.add_edge("format_response", END)

    # Add conditional edges
    workflow.add_conditional_edges(
        "validate_diagram",
        should_retry_validation,
        {
            "fix_diagram": "fix_diagram",
            "format_response": "format_response"
        }
    )

    return workflow.compile()


# Export compiled graph
class_diagram_graph = create_class_diagram_workflow()
````

---

### Step 4: Update State Schema

**File**: `workflows/class_diagram_workflow/state.py`

```python
"""
State schema for class diagram workflow.
"""

from typing import TypedDict, Optional, List, Dict, Any


class ClassDiagramState(TypedDict, total=False):
    """
    State for class diagram generation workflow.

    Fields:
        user_input: User's diagram description
        diagram_code: Generated Mermaid code (may be invalid)
        validated_diagram: Valid/fixed Mermaid code
        validation_result: Validator response
        validated: Whether diagram passed validation
        retry_count: Number of fix attempts
        errors: Validation errors
        metadata: Additional metadata
        app_context: Application context (validator, etc.)
    """
    # Input
    user_input: str

    # Generation
    diagram_code: Optional[str]

    # Validation
    validated_diagram: Optional[str]
    validation_result: Optional[Dict[str, Any]]
    validated: bool

    # Retry
    retry_count: int
    errors: Optional[List[Dict[str, Any]]]

    # Output
    metadata: Optional[Dict[str, Any]]

    # System
    app_context: Optional[Dict[str, Any]]
```

---

### Step 5: Update API Endpoint

**File**: `main.py` (update class diagram endpoint)

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import logging

from workflows.class_diagram_workflow.workflow import class_diagram_graph
from services.mermaid_validator import MermaidSubprocessManager

logger = logging.getLogger(__name__)


class DiagramRequest(BaseModel):
    """Request schema for diagram generation"""
    description: str


class DiagramResponse(BaseModel):
    """Response schema for diagram generation"""
    type: str
    detail: str
    metadata: dict


def get_validator() -> MermaidSubprocessManager:
    """Dependency to get validator from app state"""
    return app.state.validator


@app.post("/generate/class-diagram", response_model=DiagramResponse)
async def generate_class_diagram(
    request: DiagramRequest,
    validator: MermaidSubprocessManager = Depends(get_validator)
):
    """
    Generate class diagram with Mermaid validation.

    Flow:
        1. Generate diagram with LLM
        2. Validate syntax with Node.js subprocess
        3. If invalid, retry with error correction (max 3 attempts)
        4. Return diagram with validation metadata

    Args:
        request: User's diagram description
        validator: Mermaid validator instance

    Returns:
        DiagramResponse with Mermaid code and metadata

    Metadata includes:
        - validated: bool (whether validation passed)
        - retry_count: int (number of fix attempts)
        - validation_status: str ("valid" or "invalid")
        - errors: list (if validation failed after retries)
    """
    try:
        # Prepare initial state
        initial_state = {
            "user_input": request.description,
            "retry_count": 0,
            "validated": False,
            "app_context": {
                "validator": validator
            }
        }

        # Execute workflow
        logger.info(f"Generating class diagram: {request.description[:50]}...")
        result = await class_diagram_graph.ainvoke(initial_state)

        # Extract results
        diagram_code = result.get("validated_diagram") or result.get("diagram_code", "")
        metadata = result.get("metadata", {})

        if not diagram_code:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate diagram"
            )

        logger.info(
            f"✓ Diagram generated "
            f"(validated={metadata.get('validated')}, "
            f"retries={metadata.get('retry_count')})"
        )

        return DiagramResponse(
            type="class_diagram",
            detail=diagram_code,
            metadata=metadata
        )

    except Exception as e:
        logger.error(f"Failed to generate class diagram: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Diagram generation failed: {str(e)}"
        )
```

---

### Step 6: Apply to Other Workflows

Repeat the same pattern for:

**1. Use Case Diagram Workflow**

**File**: `workflows/usecase_diagram_workflow/workflow.py`

```python
# Same structure as class diagram workflow
# Update imports and node names accordingly

from .nodes.generation import generate_usecase_diagram_node
from .nodes.validation import validate_diagram_node  # Shared!
from .nodes.fix import fix_usecase_diagram_node

# ... same graph structure ...
```

**2. Activity Diagram Workflow**

**File**: `workflows/activity_diagram_workflow/workflow.py`

```python
# Same structure
from .nodes.generation import generate_activity_diagram_node
from .nodes.validation import validate_diagram_node  # Shared!
from .nodes.fix import fix_activity_diagram_node

# ... same graph structure ...
```

---

## ✅ Testing Integration

### Step 7: Integration Test

**File**: `tests/test_class_diagram_validation.py`

```python
"""
Integration tests for class diagram workflow with validation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from workflows.class_diagram_workflow.workflow import class_diagram_graph


@pytest.mark.asyncio
async def test_valid_diagram_flow():
    """Test workflow with valid diagram (no retry)"""

    # Mock validator
    mock_validator = AsyncMock()
    mock_validator.validate.return_value = {
        "valid": True,
        "code": "classDiagram\n  class User",
        "diagram_type": "classDiagram",
        "timestamp": 1699999999
    }

    initial_state = {
        "user_input": "Create a User class",
        "retry_count": 0,
        "validated": False,
        "app_context": {"validator": mock_validator}
    }

    result = await class_diagram_graph.ainvoke(initial_state)

    assert result["validated"] is True
    assert result["retry_count"] == 0
    assert "classDiagram" in result["validated_diagram"]
    assert result["metadata"]["validation_status"] == "valid"


@pytest.mark.asyncio
async def test_invalid_diagram_with_retry():
    """Test workflow with invalid diagram that gets fixed"""

    # Mock validator: first invalid, then valid
    mock_validator = AsyncMock()
    mock_validator.validate.side_effect = [
        # First validation: invalid
        {
            "valid": False,
            "code": "classDiagra\n  class User",  # Typo
            "errors": [{"message": "Unknown keyword 'classDiagra'", "line": 1}]
        },
        # Second validation: valid
        {
            "valid": True,
            "code": "classDiagram\n  class User",
            "diagram_type": "classDiagram"
        }
    ]

    initial_state = {
        "user_input": "Create a User class",
        "retry_count": 0,
        "validated": False,
        "app_context": {"validator": mock_validator}
    }

    result = await class_diagram_graph.ainvoke(initial_state)

    assert result["validated"] is True
    assert result["retry_count"] == 1  # One retry
    assert result["metadata"]["validation_status"] == "valid"


@pytest.mark.asyncio
async def test_max_retries_exceeded():
    """Test workflow when max retries exceeded"""

    # Mock validator: always invalid
    mock_validator = AsyncMock()
    mock_validator.validate.return_value = {
        "valid": False,
        "errors": [{"message": "Persistent error"}]
    }

    initial_state = {
        "user_input": "Create invalid diagram",
        "retry_count": 0,
        "validated": False,
        "app_context": {"validator": mock_validator}
    }

    result = await class_diagram_graph.ainvoke(initial_state)

    assert result["validated"] is False
    assert result["retry_count"] == 3  # Max retries
    assert result["metadata"]["validation_status"] == "invalid"
    assert "errors" in result["metadata"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## ✅ Verification Checklist

- [ ] Validation node created and tested
- [ ] Fix/retry node implemented
- [ ] Workflow graph updated with conditional edges
- [ ] State schema extended
- [ ] API endpoint updated
- [ ] Integration tests pass
- [ ] Error handling comprehensive
- [ ] Graceful degradation works
- [ ] Retry logic correctly limited to 3 attempts
- [ ] Metadata includes validation info

---

## 🎯 Commit Time!

```powershell
cd d:\Do_an_tot_nghiep\ba_copilot_ai

# Commit 1: Core integration
git add workflows/class_diagram_workflow/
git add workflows/usecase_diagram_workflow/
git add workflows/activity_diagram_workflow/
git add main.py

git commit -m "feat: integrate Mermaid validation into diagram workflows

- Add validation node to all diagram workflows
- Integrate Node.js subprocess validator
- Update state schema with validation fields
- Update API endpoints with validation
- Add graceful degradation for validator unavailability

Features:
  - Validation node checks Mermaid syntax
  - Validator injected via app_context
  - Comprehensive error handling
  - Validation results in metadata

Workflows Updated:
  - Class diagram workflow
  - Use case diagram workflow
  - Activity diagram workflow

Refs: #OPS-317"

# Commit 2: Retry logic
git add workflows/*/nodes/fix.py
git add tests/test_class_diagram_validation.py

git commit -m "feat: add retry logic for diagram error correction

- Implement fix node with LLM-based error correction
- Add conditional edges for retry logic
- Limit retries to 3 attempts
- Provide error context to LLM for intelligent fixes
- Add integration tests for retry scenarios

Features:
  - Automatic retry on validation failure
  - LLM receives error messages for context
  - Max 3 retry attempts
  - Loop: validate → fix → validate
  - Metadata tracks retry count

Tests:
  - Valid diagram (no retry)
  - Invalid diagram with successful fix
  - Max retries exceeded

Retry Strategy:
  - Lower temperature (0.3) for consistent fixes
  - Error context included in prompt
  - Markdown code extraction

Refs: #OPS-317"
```

---

## 🐛 Troubleshooting

### Issue: Infinite retry loop

**Symptom**: Workflow never completes

**Debug**:

```python
# Add logging to conditional edge
def should_retry_validation(state: ClassDiagramState) -> str:
    retry_count = state.get("retry_count", 0)
    logger.warning(f"Retry decision: count={retry_count}, validated={state.get('validated')}")
    # ... rest of logic
```

### Issue: Validator not accessible in nodes

**Symptom**:

```
KeyError: 'validator'
```

**Solution**:

```python
# Always provide validator in initial state
initial_state = {
    "user_input": description,
    "app_context": {
        "validator": app.state.validator  # Must be set!
    }
}
```

---

## 📚 Additional Resources

- [LangGraph Conditional Edges](https://langchain-ai.github.io/langgraph/how-tos/branching/)
- [LangGraph State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

---

**Next Phase**: [06_COMPREHENSIVE_TESTING.md](./06_COMPREHENSIVE_TESTING.md) →

---

**Phase 5 Complete** ✅  
**Est. Completion Time**: 60-90 minutes  
**Commits**:

1. `feat: integrate Mermaid validation into diagram workflows`
2. `feat: add retry logic for diagram error correction`
