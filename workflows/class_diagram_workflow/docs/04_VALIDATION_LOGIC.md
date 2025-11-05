# Phase 4: Validation Logic Implementation

## 🎯 Objective

Implement Mermaid diagram validation as a LangGraph node, integrate it into the class diagram workflow, and add retry logic for fixing invalid diagrams.

**Estimated Time**: 35-40 minutes  
**Commit Messages**:

1. `feat: implement Mermaid validation node in LangGraph`
2. `feat: add retry logic for invalid diagram correction`

---

## 🏗️ LangGraph Architecture Enhancement

### Current Workflow

```
[User Request] → [Generate Diagram] → [END]
```

### Enhanced Workflow with Validation

```
                    ┌──────────────────┐
                    │  User Request    │
                    └────────┬─────────┘
                             │
                             ▼
                   ┌─────────────────────┐
                   │ Generate Diagram    │
                   │ (LLM)               │
                   └─────────┬───────────┘
                             │
                             ▼
                   ┌─────────────────────┐
                   │ Validate Diagram    │
                   │ (MCP Server)        │
                   └─────────┬───────────┘
                             │
                        ┌────┴────┐
                        │ Valid?  │
                        └────┬────┘
                   ┌─────────┴─────────┐
                   │                   │
                  YES                 NO
                   │                   │
                   ▼                   ▼
            ┌──────────┐      ┌───────────────┐
            │   END    │      │  Fix Diagram  │
            └──────────┘      │  (LLM)        │
                              └───────┬───────┘
                                      │
                                      │ retry_count < 3?
                                      │
                                      ▼
                              (back to Validate)
```

**State Flow**:

1. **Generate**: LLM creates initial Mermaid code
2. **Validate**: MCP server checks syntax
3. **Decision**:
   - If valid → Return result
   - If invalid and retry_count < 3 → Fix and retry
   - If invalid and retry_count >= 3 → Return with error

---

## 🔍 Deep Dive: LangGraph State Management

### State Schema Design

**Current State** (from workflow.py):

```python
class ClassDiagramState(TypedDict):
    user_message: str
    response: dict
```

**Enhanced State**:

```python
class ClassDiagramState(TypedDict):
    user_message: str           # Original user request
    raw_diagram: str            # Initial LLM output
    validated_diagram: str      # Validated/fixed diagram
    validation_result: dict     # MCP validation response
    retry_count: int           # Number of fix attempts
    errors: list               # Validation errors
    response: dict             # Final output
```

**Why This Structure?**

| Field               | Purpose           | Used By               |
| ------------------- | ----------------- | --------------------- |
| `user_message`      | Original context  | Generate, Fix nodes   |
| `raw_diagram`       | Preserve original | Debugging, comparison |
| `validated_diagram` | Working version   | Validate, Fix nodes   |
| `validation_result` | MCP response      | Decision routing      |
| `retry_count`       | Loop control      | Conditional edge      |
| `errors`            | Error tracking    | Fix node, response    |
| `response`          | API output        | Final return          |

---

## 🛠️ Implementation Steps

### Step 1: Update State Schema

**File**: `workflows/class_diagram_workflow/workflow.py`

Replace the existing `ClassDiagramState`:

```python
# workflows/class_diagram_workflow/workflow.py
from langgraph.graph import StateGraph, END
from openai import OpenAI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.diagram import DiagramOutput, DiagramResponse
from services.mcp_client import MCPClient, MCPServerUnavailable
from typing import TypedDict, List
import logging

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")

# Configuration
MAX_RETRY_ATTEMPTS = 3


class ClassDiagramState(TypedDict):
    """
    Enhanced state schema for class diagram generation with validation.

    State Flow:
        user_message → raw_diagram → validated_diagram → response
                          ↓
                    validation_result
                          ↓
                    (retry if errors)
    """
    user_message: str               # Original user request
    raw_diagram: str               # Initial LLM-generated diagram
    validated_diagram: str         # Validated/corrected diagram
    validation_result: dict        # MCP validation response
    retry_count: int              # Number of fix attempts
    errors: List[str]             # Accumulated error messages
    response: dict                # Final API response
```

**Key Design Decision**: Why separate `raw_diagram` and `validated_diagram`?

```python
# Scenario: LLM generates diagram, validation fails, fix applied
state = {
    "raw_diagram": "graph TD\nA--INVALID-->B",  # Original (for debugging)
    "validated_diagram": "graph TD\nA-->B",     # After fix (for output)
    "validation_result": {"valid": True},
    "retry_count": 1
}
```

**Benefits**:

- ✅ **Debugging**: Can compare original vs. fixed
- ✅ **Metrics**: Track how often fixes are needed
- ✅ **Transparency**: Show users what was changed

---

### Step 2: Create Validation Node

Add the validation function:

```python
async def validate_diagram_node(state: ClassDiagramState) -> ClassDiagramState:
    """
    Validate Mermaid diagram using MCP server.

    This node:
    1. Takes diagram from state (raw_diagram or validated_diagram)
    2. Sends to MCP server for syntax validation
    3. Updates state with validation results
    4. Handles MCP server unavailability gracefully

    Args:
        state: Current workflow state

    Returns:
        Updated state with validation_result

    State Updates:
        - validation_result: Dict with 'valid', 'code', 'errors'
        - errors: Appends validation errors if invalid
    """
    logger.info("Validating Mermaid diagram...")

    # Get diagram to validate (use validated_diagram if exists, else raw_diagram)
    diagram_code = state.get("validated_diagram") or state.get("raw_diagram", "")

    if not diagram_code:
        logger.error("No diagram code to validate")
        return {
            **state,
            "validation_result": {
                "valid": False,
                "code": "",
                "errors": ["No diagram code provided"]
            },
            "errors": state.get("errors", []) + ["No diagram code provided"]
        }

    try:
        # Validate using MCP client
        async with MCPClient() as client:
            validation_result = await client.validate_mermaid(diagram_code)

        logger.info(f"Validation result: valid={validation_result['valid']}")

        # Update state with validation result
        new_errors = state.get("errors", [])
        if not validation_result["valid"]:
            new_errors.extend(validation_result.get("errors", []))

        return {
            **state,
            "validation_result": validation_result,
            "errors": new_errors,
            "validated_diagram": diagram_code  # Keep current diagram
        }

    except MCPServerUnavailable as e:
        # Graceful degradation: MCP server unavailable
        logger.warning(f"MCP server unavailable: {e}")
        logger.warning("Proceeding with unvalidated diagram")

        return {
            **state,
            "validation_result": {
                "valid": True,  # Assume valid to proceed
                "code": diagram_code,
                "errors": [],
                "warning": "MCP server unavailable, diagram not validated"
            },
            "validated_diagram": diagram_code
        }

    except Exception as e:
        # Unexpected error
        logger.error(f"Validation error: {e}", exc_info=True)

        return {
            **state,
            "validation_result": {
                "valid": False,
                "code": diagram_code,
                "errors": [f"Validation error: {str(e)}"]
            },
            "errors": state.get("errors", []) + [f"Validation error: {str(e)}"]
        }
```

**Error Handling Strategy**:

| Error Type                 | Handling                  | Rationale            |
| -------------------------- | ------------------------- | -------------------- |
| **No diagram code**        | Invalid, add error        | Cannot proceed       |
| **MCP server unavailable** | Assume valid, add warning | Graceful degradation |
| **Validation fails**       | Invalid, add errors       | Expected flow        |
| **Unexpected error**       | Invalid, add error        | Safe failure         |

**Async vs. Sync**:

```python
# Why async?
async def validate_diagram_node(state: ClassDiagramState):
    async with MCPClient() as client:  # Non-blocking HTTP call
        result = await client.validate_mermaid(code)
```

**Problem**: LangGraph nodes can be sync or async, but we need async for `httpx`.

**Solution**: LangGraph automatically handles async nodes! No changes needed to graph setup.

---

### Step 3: Update Generation Node

Modify the existing generation function to populate `raw_diagram`:

````python
def generate_class_diagram_description(state: ClassDiagramState) -> ClassDiagramState:
    """
    Generate class diagram in Mermaid format using OpenRouter AI.

    Updated to populate raw_diagram for validation workflow.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    prompt = f"""
    Create a detailed UML Class Diagram in Mermaid markdown format based on the requirement: {state['user_message']}

    The diagram should include:
    - Classes with their attributes (name, type, visibility: +public, -private, #protected)
    - Methods/Operations for each class (name, parameters, return type, visibility)
    - Relationships between classes:
      * Association (simple connection between classes)
      * Aggregation (has-a relationship, hollow diamond)
      * Composition (strong ownership, filled diamond)
      * Inheritance (is-a relationship, hollow arrow)
      * Dependency (uses, dashed arrow)
      * Multiplicity (1, 0..1, 1..*, 0..*, etc.)
    - Abstract classes and interfaces if applicable
    - Key design patterns if relevant

    IMPORTANT: Return ONLY the Mermaid markdown code block for the class diagram, starting with ```mermaid and ending with ```.
    Do not include any explanatory text before or after the code block.

    Example format:
    ```mermaid
    classDiagram
        class ClassName {{
            +String attribute
            -int privateAttribute
            +method()
        }}
        ClassA --|> ClassB : Inheritance
        ClassC --* ClassD : Composition
    ```
    """

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "BA-Copilot",
            },
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        markdown_diagram = completion.choices[0].message.content

        logger.info(f"Generated diagram: {len(markdown_diagram)} characters")

        # Return state with raw_diagram populated
        return {
            **state,
            "raw_diagram": markdown_diagram,
            "validated_diagram": markdown_diagram,  # Initially same as raw
            "retry_count": 0,
            "errors": []
        }

    except Exception as e:
        logger.error(f"Error generating class diagram: {e}", exc_info=True)

        # Return error state
        return {
            **state,
            "raw_diagram": "",
            "validated_diagram": "",
            "retry_count": 0,
            "errors": [f"Generation error: {str(e)}"],
            "response": {
                "type": "class_diagram",
                "detail": f"Error generating class diagram: {str(e)}"
            }
        }
````

**Changes Made**:

1. ✅ Populate `raw_diagram` with LLM output
2. ✅ Initialize `validated_diagram` (same as raw initially)
3. ✅ Initialize `retry_count` to 0
4. ✅ Initialize `errors` list
5. ✅ Add logging for observability

---

### Step 4: Create Fix Diagram Node

Add a new node to fix invalid diagrams:

````python
def fix_diagram_node(state: ClassDiagramState) -> ClassDiagramState:
    """
    Attempt to fix invalid Mermaid diagram using LLM.

    This node:
    1. Takes the invalid diagram and error messages
    2. Asks LLM to fix the syntax errors
    3. Increments retry_count
    4. Updates validated_diagram with fixed version

    Args:
        state: Current workflow state (must have validation errors)

    Returns:
        Updated state with fixed diagram

    State Updates:
        - validated_diagram: Fixed diagram code
        - retry_count: Incremented
    """
    logger.info(f"Attempting to fix diagram (retry {state.get('retry_count', 0) + 1}/{MAX_RETRY_ATTEMPTS})...")

    # Get current diagram and errors
    diagram_code = state.get("validated_diagram", state.get("raw_diagram", ""))
    errors = state.get("errors", [])
    user_message = state.get("user_message", "")

    if not errors:
        logger.warning("Fix node called but no errors present")
        return state

    # Construct fix prompt
    errors_text = "\n".join(f"- {error}" for error in errors)

    fix_prompt = f"""
    The following Mermaid class diagram has syntax errors:

    ```mermaid
    {diagram_code}
    ```

    Errors:
    {errors_text}

    Original requirement: {user_message}

    Please fix the diagram to be syntactically correct Mermaid code.

    Requirements:
    1. Fix all syntax errors
    2. Maintain the original intent and structure
    3. Ensure valid Mermaid classDiagram syntax
    4. Return ONLY the corrected Mermaid code block (```mermaid ... ```)

    Do not add explanations or comments outside the code block.
    """

    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "BA-Copilot",
            },
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[
                {
                    "role": "user",
                    "content": fix_prompt
                }
            ]
        )

        fixed_diagram = completion.choices[0].message.content

        logger.info(f"Fixed diagram: {len(fixed_diagram)} characters")

        return {
            **state,
            "validated_diagram": fixed_diagram,
            "retry_count": state.get("retry_count", 0) + 1,
            # Clear errors for re-validation
            "errors": []
        }

    except Exception as e:
        logger.error(f"Error fixing diagram: {e}", exc_info=True)

        return {
            **state,
            "retry_count": state.get("retry_count", 0) + 1,
            "errors": state.get("errors", []) + [f"Fix error: {str(e)}"]
        }
````

**Fix Strategy Explained**:

1. **Context Preservation**:

   ```python
   fix_prompt = f"""
   Original requirement: {user_message}
   ```

   - **Why**: LLM needs original context to maintain intent
   - **Without it**: May oversimplify or change structure

2. **Error Details**:

   ```python
   errors_text = "\n".join(f"- {error}" for error in errors)
   ```

   - **Specific errors**: Better than "something is wrong"
   - **Example**: "Line 5: Invalid arrow syntax '--INVALID-->'"

3. **Retry Counter**:
   ```python
   "retry_count": state.get("retry_count", 0) + 1
   ```
   - **Purpose**: Track how many fix attempts
   - **Used by**: Conditional edge to limit retries

---

### Step 5: Create Format Response Node

Add final formatting node:

```python
def format_response_node(state: ClassDiagramState) -> ClassDiagramState:
    """
    Format final response with validation metadata.

    This node:
    1. Takes validated diagram from state
    2. Adds validation metadata
    3. Formats response according to API schema

    Args:
        state: Final workflow state

    Returns:
        State with formatted response
    """
    logger.info("Formatting final response...")

    diagram_code = state.get("validated_diagram", state.get("raw_diagram", ""))
    validation_result = state.get("validation_result", {})
    retry_count = state.get("retry_count", 0)
    errors = state.get("errors", [])

    # Build response metadata
    metadata = {
        "validated": validation_result.get("valid", False),
        "retry_count": retry_count,
    }

    # Add warnings if any
    if "warning" in validation_result:
        metadata["warning"] = validation_result["warning"]

    # Add errors if final result is invalid
    if not validation_result.get("valid", False) and errors:
        metadata["errors"] = errors
        metadata["note"] = f"Diagram may have syntax errors after {retry_count} fix attempts"

    # Create response
    diagram_response = DiagramResponse(
        type="class_diagram",
        detail=diagram_code,
        metadata=metadata  # Add metadata field
    )

    output = DiagramOutput(type="diagram", response=diagram_response)

    return {
        **state,
        "response": output.model_dump()["response"]
    }
```

**Response Schema Update Needed**:

We need to update `models/diagram.py` to include metadata:

```python
# models/diagram.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class DiagramResponse(BaseModel):
    type: str  # "class_diagram" or "usecase_diagram"
    detail: str  # Markdown content of the diagram
    metadata: Optional[Dict[str, Any]] = None  # Validation metadata

class DiagramOutput(BaseModel):
    type: str
    response: DiagramResponse
```

---

### Step 6: Create Conditional Edge Function

Define routing logic:

```python
def should_retry_fix(state: ClassDiagramState) -> str:
    """
    Conditional edge to determine if diagram should be retried.

    Decision logic:
    - If valid → Go to format_response
    - If invalid and retry_count < MAX_RETRY_ATTEMPTS → Go to fix_diagram
    - If invalid and retry_count >= MAX_RETRY_ATTEMPTS → Go to format_response (give up)

    Args:
        state: Current workflow state

    Returns:
        Next node name: "fix_diagram" or "format_response"
    """
    validation_result = state.get("validation_result", {})
    retry_count = state.get("retry_count", 0)

    is_valid = validation_result.get("valid", False)

    if is_valid:
        logger.info("Diagram is valid, proceeding to format response")
        return "format_response"

    if retry_count < MAX_RETRY_ATTEMPTS:
        logger.info(f"Diagram invalid, attempting fix (retry {retry_count + 1}/{MAX_RETRY_ATTEMPTS})")
        return "fix_diagram"

    logger.warning(f"Max retry attempts reached ({MAX_RETRY_ATTEMPTS}), returning invalid diagram")
    return "format_response"
```

**Decision Tree**:

```
Validation Result
      │
      ├─ Valid? ────────────────► format_response ─► END
      │
      └─ Invalid?
            │
            ├─ retry_count < 3? ─► fix_diagram ─► validate_diagram (loop)
            │
            └─ retry_count >= 3? ► format_response ─► END (with errors)
```

---

### Step 7: Build Enhanced Workflow Graph

Replace the existing workflow construction:

```python
# Build LangGraph pipeline for Class Diagram with Validation
workflow = StateGraph(ClassDiagramState)

# Add nodes
workflow.add_node("generate_class_diagram", generate_class_diagram_description)
workflow.add_node("validate_diagram", validate_diagram_node)
workflow.add_node("fix_diagram", fix_diagram_node)
workflow.add_node("format_response", format_response_node)

# Set entry point
workflow.set_entry_point("generate_class_diagram")

# Add edges
workflow.add_edge("generate_class_diagram", "validate_diagram")

# Conditional edge after validation
workflow.add_conditional_edges(
    "validate_diagram",
    should_retry_fix,
    {
        "fix_diagram": "fix_diagram",
        "format_response": "format_response"
    }
)

# After fix, go back to validation
workflow.add_edge("fix_diagram", "validate_diagram")

# Final edge
workflow.add_edge("format_response", END)

# Compile graph
class_diagram_graph = workflow.compile()
```

**Graph Visualization**:

```
START
  │
  ▼
generate_class_diagram
  │
  ▼
validate_diagram ◄─┐
  │                │
  ▼                │
[Conditional]      │
  │                │
  ├─ valid ────────┼─► format_response ─► END
  │                │
  └─ invalid       │
      │            │
      ▼            │
  fix_diagram ─────┘
```

**Cycle Detection**: LangGraph allows cycles (fix → validate → fix), but we control it with `retry_count`.

---

### Step 8: Update models/diagram.py

**File**: `models/diagram.py`

```python
# models/diagram.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class DiagramResponse(BaseModel):
    """
    Response model for diagram generation.

    Attributes:
        type: Diagram type (class_diagram, usecase_diagram, etc.)
        detail: Mermaid markdown code
        metadata: Optional validation and processing metadata
    """
    type: str = Field(..., description="Type of diagram")
    detail: str = Field(..., description="Mermaid diagram code")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Validation metadata including validated status, retry count, warnings, errors"
    )

class DiagramOutput(BaseModel):
    """
    Top-level output model for diagram API responses.
    """
    type: str = Field(..., description="Response type (always 'diagram')")
    response: DiagramResponse = Field(..., description="Diagram response data")
```

---

### Step 9: Test the Enhanced Workflow

Create a test script:

**File**: `test_validation_workflow.py` (temporary)

```python
"""
Test script for validation workflow.
Usage: python test_validation_workflow.py
"""

import asyncio
from workflows.class_diagram_workflow import class_diagram_graph

async def test_valid_diagram():
    """Test with a request that should generate valid diagram"""
    print("Test 1: Valid Diagram Generation")
    print("="*50)

    result = class_diagram_graph.invoke({
        "user_message": "Create a simple User class with name and email attributes"
    })

    response = result["response"]
    print(f"Type: {response['type']}")
    print(f"Validated: {response.get('metadata', {}).get('validated', 'N/A')}")
    print(f"Retry Count: {response.get('metadata', {}).get('retry_count', 0)}")
    print(f"Diagram Length: {len(response['detail'])} characters")
    print()

async def test_complex_diagram():
    """Test with complex requirements"""
    print("Test 2: Complex Diagram with Validation")
    print("="*50)

    result = class_diagram_graph.invoke({
        "user_message": "Create class diagram for e-commerce system with User, Product, Order, and Payment classes with relationships"
    })

    response = result["response"]
    print(f"Type: {response['type']}")
    print(f"Validated: {response.get('metadata', {}).get('validated', 'N/A')}")
    print(f"Retry Count: {response.get('metadata', {}).get('retry_count', 0)}")

    if response.get('metadata', {}).get('errors'):
        print(f"Errors: {response['metadata']['errors']}")

    print(f"Diagram:\n{response['detail'][:200]}...")
    print()

async def main():
    await test_valid_diagram()
    await test_complex_diagram()

if __name__ == "__main__":
    asyncio.run(main())
```

**Run tests**:

```powershell
# Ensure MCP server is running
docker-compose up mcp-server -d

# Run test
python test_validation_workflow.py
```

**Expected Output**:

````
Test 1: Valid Diagram Generation
==================================================
Type: class_diagram
Validated: True
Retry Count: 0
Diagram Length: 245 characters

Test 2: Complex Diagram with Validation
==================================================
Type: class_diagram
Validated: True
Retry Count: 1
Diagram:
```mermaid
classDiagram
    class User {
        +String name
        +String email
        +login()
    }
...
````

---

## ✅ Verification Checklist

Before proceeding to Phase 5, ensure:

- [ ] State schema updated with all required fields
- [ ] `validate_diagram_node` created and handles errors gracefully
- [ ] `fix_diagram_node` created with retry logic
- [ ] `format_response_node` adds validation metadata
- [ ] Conditional edge `should_retry_fix` implemented
- [ ] Workflow graph updated with all nodes and edges
- [ ] `models/diagram.py` updated with metadata field
- [ ] Test script runs successfully
- [ ] Valid diagrams pass validation
- [ ] Invalid diagrams trigger retry and fix

---

## 🎯 Commit Time!

**Commit 1**: Core validation logic

```powershell
git add workflows/class_diagram_workflow/workflow.py
git add models/diagram.py
git add services/mcp_client.py

git commit -m "feat: implement Mermaid validation node in LangGraph

- Add enhanced state schema with validation fields
- Create validate_diagram_node for MCP integration
- Update DiagramResponse model with metadata field
- Implement graceful degradation for MCP unavailability
- Add comprehensive logging for observability

State fields added:
- raw_diagram: Original LLM output
- validated_diagram: Validated/fixed version
- validation_result: MCP validation response
- retry_count: Number of fix attempts
- errors: Accumulated error messages

Refs: #OPS-266"
```

**Commit 2**: Retry and fix logic

```powershell
git add workflows/class_diagram_workflow/workflow.py
git add test_validation_workflow.py

git commit -m "feat: add retry logic for invalid diagram correction

- Create fix_diagram_node to correct syntax errors
- Implement should_retry_fix conditional edge
- Add MAX_RETRY_ATTEMPTS configuration (3 attempts)
- Create format_response_node for final output
- Build complete workflow graph with validation cycle

Workflow: generate → validate → [fix if invalid] → format → END

Features:
- Auto-retry up to 3 times for invalid diagrams
- LLM-powered error correction
- Detailed error messages in response
- Validation metadata in API output

Refs: #OPS-266"
```

---

## 🐛 Troubleshooting

### Issue: LangGraph async node not executing

**Symptom**: Validation node skipped or sync execution

**Solution**: Ensure LangGraph version supports async nodes

```powershell
pip install --upgrade langgraph>=0.0.52
```

### Issue: Fix loop never terminates

**Symptom**: Workflow hangs in fix → validate loop

**Debug**:

```python
# Add logging in conditional edge
def should_retry_fix(state: ClassDiagramState) -> str:
    retry_count = state.get("retry_count", 0)
    print(f"DEBUG: retry_count={retry_count}, MAX={MAX_RETRY_ATTEMPTS}")
    ...
```

**Solution**: Verify `retry_count` increments correctly in `fix_diagram_node`

### Issue: Metadata not appearing in response

**Symptom**: `response.metadata` is `None`

**Debug**:

```python
# Check Pydantic model excludes None
class DiagramResponse(BaseModel):
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        exclude_none = False  # Include None values
```

---

## 📚 Additional Resources

- [LangGraph State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)
- [LangGraph Conditional Edges](https://langchain-ai.github.io/langgraph/how-tos/branching/)
- [Pydantic Models](https://docs.pydantic.dev/latest/usage/models/)
- [Python AsyncIO](https://docs.python.org/3/library/asyncio.html)

---

**Next Phase**: [05_INTEGRATION_TESTING.md](./05_INTEGRATION_TESTING.md) →

---

**Phase 4 Complete** ✅  
**Est. Completion Time**: 35-40 minutes  
**Commits**:

- `feat: implement Mermaid validation node in LangGraph`
- `feat: add retry logic for invalid diagram correction`
