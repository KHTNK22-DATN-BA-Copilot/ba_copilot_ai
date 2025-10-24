# Guideline Tích Hợp FigmaMCP vào BA Copilot

## 1. Tổng Quan

FigmaMCP (Figma Model Context Protocol) là module tích hợp cho phép BA Copilot tự động tạo wireframe và diagram thông qua Figma API. Module này được thiết kế để làm việc với LangGraph workflow orchestration.

### Chức năng chính:
- **Wireframe Generation**: Tự động tạo wireframe/mockup giao diện
- **Diagram Generation**: Tự động tạo các loại sơ đồ (ERD, Architecture, Flowchart, Sequence Diagram)
- **Figma Integration**: Kết nối với Figma API để tạo và quản lý design files

## 2. Kiến Trúc Hệ Thống

```
User Request
    ↓
FastAPI Endpoint (/ai/generate)
    ↓
AI Workflow (ai_workflow.py)
    ↓
Intent Classification
    ↓
┌─────────────┴─────────────┐
↓                           ↓
Wireframe Workflow      Diagram Workflow
    ↓                       ↓
figma_mcp.py           figma_mcp.py
    ↓                       ↓
Figma API              Figma API
```

## 3. Cấu Trúc File Hiện Tại

```
AI_Implement/
├── figma_mcp.py                    # Module chính FigmaMCP
├── wireframe_workflow/
│   ├── __init__.py
│   └── workflow.py                 # LangGraph workflow cho wireframe
├── diagram_workflow/
│   ├── __init__.py
│   └── workflow.py                 # LangGraph workflow cho diagram
├── models/
│   ├── wireframe.py                # Pydantic models cho wireframe
│   └── diagram.py                  # Pydantic models cho diagram
└── ai_workflow.py                  # Main workflow orchestrator
```

## 4. Chi Tiết Implementation

### 4.1. FigmaMCP Module ([figma_mcp.py](figma_mcp.py))

**Chức năng hiện tại:**
```python
def generate_figma_wireframe(description: str) -> dict:
    """
    Tạo wireframe mock với UUID và link Figma

    Args:
        description: Mô tả yêu cầu wireframe

    Returns:
        dict: {
            "figma_link": str,
            "editable": bool,
            "description": str
        }
    """

def generate_figma_diagram(description: str) -> dict:
    """
    Tạo diagram mock với UUID và link Figma

    Args:
        description: Mô tả yêu cầu diagram

    Returns:
        dict: {
            "figma_link": str,
            "editable": bool,
            "description": str
        }
    """
```

**Trạng thái:** Hiện tại đang là mock implementation với UUID ngẫu nhiên.

### 4.2. Wireframe Workflow ([wireframe_workflow/workflow.py](wireframe_workflow/workflow.py))

```python
class WireframeState(TypedDict):
    user_message: str  # Input từ user
    response: dict     # Output wireframe data

# LangGraph Flow:
# 1. Nhận user_message
# 2. Gọi generate_figma_wireframe() từ figma_mcp.py
# 3. Validate với WireframeResponse model
# 4. Trả về response
```

### 4.3. Diagram Workflow ([diagram_workflow/workflow.py](diagram_workflow/workflow.py))

```python
class DiagramState(TypedDict):
    user_message: str  # Input từ user
    response: dict     # Output diagram data

# LangGraph Flow:
# 1. Nhận user_message
# 2. Gọi OpenRouter AI để tạo mô tả chi tiết
# 3. Gọi generate_figma_diagram() từ figma_mcp.py
# 4. Validate với DiagramResponse model
# 5. Trả về response
```

## 5. Hướng Dẫn Tích Hợp Thực Sự với Figma API

### 5.1. Yêu Cầu

1. **Figma Account**: Tạo tài khoản tại [figma.com](https://www.figma.com)
2. **Figma Access Token**:
   - Vào Settings → Personal access tokens
   - Tạo token mới với quyền `file:write`
3. **Figma Team ID**: Lấy từ URL team của bạn

### 5.2. Cài Đặt Dependencies

Thêm vào [requirements.txt](requirements.txt):
```text
# Figma Integration
pyfigma>=0.1.0           # Figma Python SDK
requests>=2.31.0         # HTTP client
pillow>=10.0.0           # Image processing (nếu cần)
```

Cài đặt:
```bash
pip install -r requirements.txt
```

### 5.3. Cấu Hình Environment Variables

Thêm vào [.env](.env):
```env
# Figma Configuration
FIGMA_ACCESS_TOKEN=your_figma_personal_access_token
FIGMA_TEAM_ID=your_team_id
FIGMA_PROJECT_ID=your_project_id_for_auto_generated_files

# Optional: Template files
FIGMA_WIREFRAME_TEMPLATE_ID=template_file_key
FIGMA_DIAGRAM_TEMPLATE_ID=template_file_key
```

Thêm vào [.env.example](.env.example):
```env
FIGMA_ACCESS_TOKEN=figd_xxxxxxxxxxxx
FIGMA_TEAM_ID=123456789
FIGMA_PROJECT_ID=987654321
FIGMA_WIREFRAME_TEMPLATE_ID=
FIGMA_DIAGRAM_TEMPLATE_ID=
```

### 5.4. Nâng Cấp figma_mcp.py

**Bước 1:** Import thư viện cần thiết
```python
# figma_mcp.py
import os
import requests
from typing import Dict, Optional
from datetime import datetime

# Figma API Configuration
FIGMA_API_BASE = "https://api.figma.com/v1"
FIGMA_ACCESS_TOKEN = os.getenv("FIGMA_ACCESS_TOKEN")
FIGMA_TEAM_ID = os.getenv("FIGMA_TEAM_ID")
FIGMA_PROJECT_ID = os.getenv("FIGMA_PROJECT_ID")

# Headers cho Figma API
HEADERS = {
    "X-Figma-Token": FIGMA_ACCESS_TOKEN,
    "Content-Type": "application/json"
}
```

**Bước 2:** Implement hàm tạo file Figma thực sự
```python
def create_figma_file(name: str, project_id: Optional[str] = None) -> Dict:
    """
    Tạo file Figma mới

    Args:
        name: Tên file
        project_id: ID của project (optional)

    Returns:
        dict: Thông tin file đã tạo
    """
    url = f"{FIGMA_API_BASE}/files"

    payload = {
        "name": name,
        "team_id": FIGMA_TEAM_ID
    }

    if project_id:
        payload["project_id"] = project_id

    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()

    return response.json()

def update_figma_file_content(file_key: str, components: list) -> Dict:
    """
    Cập nhật nội dung file Figma với components

    Args:
        file_key: Key của file Figma
        components: List các components để thêm vào

    Returns:
        dict: Kết quả update
    """
    url = f"{FIGMA_API_BASE}/files/{file_key}"

    # Tạo canvas với components
    payload = {
        "document": {
            "children": components
        }
    }

    response = requests.put(url, headers=HEADERS, json=payload)
    response.raise_for_status()

    return response.json()

def get_figma_file_link(file_key: str) -> str:
    """
    Tạo link để xem/edit file Figma

    Args:
        file_key: Key của file

    Returns:
        str: URL đầy đủ
    """
    return f"https://www.figma.com/file/{file_key}"
```

**Bước 3:** Cập nhật generate_figma_wireframe()
```python
def generate_figma_wireframe(description: str) -> Dict:
    """
    Tạo wireframe thực sự trên Figma

    Args:
        description: Mô tả yêu cầu wireframe từ user

    Returns:
        dict: Thông tin wireframe đã tạo
    """
    try:
        # Tạo tên file với timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"Wireframe_{timestamp}"

        # Tạo file mới trên Figma
        file_data = create_figma_file(
            name=file_name,
            project_id=FIGMA_PROJECT_ID
        )

        file_key = file_data.get("key")

        # TODO: Sử dụng AI để generate wireframe components
        # Có thể tích hợp với LLM để parse description và tạo components

        # Tạo basic components (ví dụ)
        components = create_wireframe_components(description)

        # Update file với components
        update_figma_file_content(file_key, components)

        # Tạo link
        figma_link = get_figma_file_link(file_key)

        return {
            "figma_link": figma_link,
            "editable": True,
            "description": description,
            "file_key": file_key,
            "created_at": timestamp
        }

    except Exception as e:
        print(f"Error creating Figma wireframe: {e}")
        # Fallback về mock nếu có lỗi
        import uuid
        figma_id = uuid.uuid4()
        return {
            "figma_link": f"https://www.figma.com/file/{figma_id}/auto-generated-wireframe",
            "editable": False,
            "description": f"Error: {str(e)}"
        }

def create_wireframe_components(description: str) -> list:
    """
    Parse description và tạo Figma components tương ứng

    Args:
        description: Mô tả wireframe

    Returns:
        list: Danh sách Figma components
    """
    # TODO: Implement AI-powered component generation
    # Ví dụ đơn giản:
    components = [
        {
            "type": "FRAME",
            "name": "Wireframe Canvas",
            "children": [
                {
                    "type": "RECTANGLE",
                    "name": "Header",
                    "fills": [{"type": "SOLID", "color": {"r": 0.9, "g": 0.9, "b": 0.9}}]
                },
                {
                    "type": "TEXT",
                    "name": "Title",
                    "characters": description[:50]
                }
            ]
        }
    ]

    return components
```

**Bước 4:** Cập nhật generate_figma_diagram() tương tự
```python
def generate_figma_diagram(description: str) -> Dict:
    """
    Tạo diagram thực sự trên Figma (ERD, Flowchart, Architecture)

    Args:
        description: Mô tả chi tiết diagram từ AI

    Returns:
        dict: Thông tin diagram đã tạo
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"Diagram_{timestamp}"

        file_data = create_figma_file(
            name=file_name,
            project_id=FIGMA_PROJECT_ID
        )

        file_key = file_data.get("key")

        # Parse description và tạo diagram components
        components = create_diagram_components(description)

        update_figma_file_content(file_key, components)

        figma_link = get_figma_file_link(file_key)

        return {
            "figma_link": figma_link,
            "editable": True,
            "description": description,
            "file_key": file_key,
            "created_at": timestamp
        }

    except Exception as e:
        print(f"Error creating Figma diagram: {e}")
        import uuid
        figma_id = uuid.uuid4()
        return {
            "figma_link": f"https://www.figma.com/file/{figma_id}/auto-generated-diagram",
            "editable": False,
            "description": f"Error: {str(e)}"
        }

def create_diagram_components(description: str) -> list:
    """
    Parse AI description và tạo diagram components

    Args:
        description: Mô tả diagram chi tiết từ AI

    Returns:
        list: Figma components cho diagram
    """
    # TODO: Implement sophisticated diagram parsing
    # Có thể tích hợp với structured output từ LLM

    components = [
        {
            "type": "FRAME",
            "name": "Diagram Canvas",
            "children": []  # Add diagram elements
        }
    ]

    return components
```

### 5.5. Nâng Cấp với AI-Powered Generation

**Tích hợp với LLM để tạo structured components:**

```python
# figma_mcp.py
from openai import OpenAI
import json

def ai_generate_wireframe_structure(description: str) -> dict:
    """
    Sử dụng AI để tạo cấu trúc wireframe từ description

    Args:
        description: Yêu cầu wireframe từ user

    Returns:
        dict: Cấu trúc wireframe JSON
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPEN_ROUTER_API_KEY"),
    )

    prompt = f"""
    Based on this wireframe requirement: "{description}"

    Generate a JSON structure for Figma components including:
    - Layout structure (header, sidebar, content, footer)
    - UI elements (buttons, inputs, cards, etc.)
    - Positions and sizes
    - Text content

    Return ONLY valid JSON in this format:
    {{
        "components": [
            {{
                "type": "FRAME",
                "name": "Component Name",
                "x": 0,
                "y": 0,
                "width": 375,
                "height": 800,
                "children": []
            }}
        ]
    }}
    """

    response = client.chat.completions.create(
        model="tngtech/deepseek-r1t2-chimera:free",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
```

## 6. Testing

### 6.1. Test Mock Version (Hiện Tại)

```bash
# Test wireframe generation
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tạo wireframe cho trang đăng nhập với email, password và nút đăng nhập"
  }'

# Test diagram generation
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tạo ERD cho hệ thống quản lý thư viện"
  }'
```

### 6.2. Test Real Figma Integration

```bash
# Test với Figma API credentials
export FIGMA_ACCESS_TOKEN="your_token"
export FIGMA_TEAM_ID="your_team_id"
export FIGMA_PROJECT_ID="your_project_id"

# Test create file
python -c "from figma_mcp import create_figma_file; print(create_figma_file('Test File'))"

# Test full workflow
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tạo wireframe cho dashboard quản lý"
  }'
```

### 6.3. Unit Tests

Tạo file `tests/test_figma_mcp.py`:
```python
import pytest
from figma_mcp import generate_figma_wireframe, generate_figma_diagram

def test_wireframe_generation():
    result = generate_figma_wireframe("Login page")

    assert "figma_link" in result
    assert "editable" in result
    assert "description" in result
    assert result["editable"] == True

def test_diagram_generation():
    result = generate_figma_diagram("ERD for library system")

    assert "figma_link" in result
    assert "editable" in result
    assert "description" in result

def test_error_handling():
    # Test với invalid input
    result = generate_figma_wireframe("")
    assert "figma_link" in result
```

## 7. Roadmap Nâng Cấp

### Phase 1: Mock Implementation ✅ (Hiện Tại)
- [x] Mock wireframe generation với UUID
- [x] Mock diagram generation với UUID
- [x] LangGraph workflow integration
- [x] Pydantic models validation

### Phase 2: Real Figma API Integration 🔄 (Đang Thực Hiện)
- [ ] Tích hợp Figma REST API
- [ ] Tạo file thực sự trên Figma
- [ ] Quản lý projects và teams
- [ ] Error handling và retry logic

### Phase 3: AI-Powered Generation 🎯 (Kế Hoạch)
- [ ] LLM tạo wireframe components từ description
- [ ] LLM tạo diagram structure từ requirements
- [ ] Template-based generation
- [ ] Component library integration

### Phase 4: Advanced Features 🚀 (Tương Lai)
- [ ] Real-time collaboration
- [ ] Version control
- [ ] Export to code (React, Vue, etc.)
- [ ] Design system integration
- [ ] Figma plugin development

## 8. Best Practices

### 8.1. Security
- **Không commit** `.env` file
- Sử dụng environment variables cho sensitive data
- Rotate Figma access tokens định kỳ
- Giới hạn permissions của tokens

### 8.2. Error Handling
- Luôn có fallback khi Figma API fail
- Log errors chi tiết để debug
- Retry logic cho network failures
- User-friendly error messages

### 8.3. Performance
- Cache Figma API responses khi có thể
- Batch operations khi tạo nhiều components
- Async/await cho I/O operations
- Rate limiting để tránh API quota

### 8.4. Code Organization
```
figma_mcp/
├── __init__.py
├── client.py          # Figma API client
├── generators.py      # Wireframe/diagram generators
├── components.py      # Figma component builders
├── templates.py       # Template management
└── utils.py          # Helper functions
```

## 9. Troubleshooting

### 9.1. Figma API Errors

**401 Unauthorized:**
```
- Kiểm tra FIGMA_ACCESS_TOKEN trong .env
- Verify token còn valid tại Figma Settings
- Ensure token có đủ permissions
```

**404 Not Found:**
```
- Kiểm tra FIGMA_TEAM_ID và FIGMA_PROJECT_ID
- Verify user có access vào team/project
```

**429 Rate Limit:**
```
- Implement exponential backoff
- Sử dụng caching
- Giảm số lượng API calls
```

### 9.2. LangGraph Workflow Issues

**Workflow không chạy:**
```
- Check logs: docker-compose logs -f ai-service
- Verify workflow compilation: workflow.compile()
- Debug state transitions
```

**Response format không đúng:**
```
- Validate với Pydantic models
- Check model_dump() output
- Verify TypedDict structure
```

## 10. Resources

### Documentation
- [Figma API Docs](https://www.figma.com/developers/api)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Tutorials
- [Figma API Getting Started](https://www.figma.com/developers/api#getting-started)
- [Building with LangGraph](https://python.langchain.com/docs/langgraph)

### Community
- [Figma Developer Community](https://forum.figma.com/c/developers/8)
- [LangChain Discord](https://discord.gg/langchain)

---

## Contact & Support

Nếu có vấn đề hoặc câu hỏi về tích hợp FigmaMCP:
1. Check [ARCHITECTURE.md](ARCHITECTURE.md) để hiểu kiến trúc hệ thống
2. Review [README.md](README.md) cho setup instructions
3. See [TROUBLESHOOTING](#9-troubleshooting) section
4. Tạo issue trong repository

**Version:** 1.0.0
**Last Updated:** 2025-10-24
