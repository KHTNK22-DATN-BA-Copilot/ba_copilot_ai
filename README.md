# BA Copilot - AI Service

AI Service cho BA Copilot, cung cấp các chức năng:
- **Generate SRS**: Tạo tài liệu Software Requirements Specification
- **Generate Wireframe**: Tạo wireframe/mockup giao diện
- **Generate Diagram**: Tạo sơ đồ ERD, Architecture, Flowchart

## Tech Stack

- **FastAPI**: Web framework
- **LangGraph**: Workflow orchestration
- **LangChain**: LLM integration
- **Google Gemini**: AI model
- **Docker**: Containerization
- **PostgreSQL**: Database

## Setup

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình environment variables

Copy `.env.example` thành `.env` và điền thông tin:

```bash
cp .env.example .env
```

Chỉnh sửa `.env`:
```env
GOOGLE_API_KEY=your_actual_google_api_key_here
```

Lấy Google API Key tại: https://makersuite.google.com/app/apikey

### 3. Chạy bằng Docker

```bash
# Build và start services
docker-compose up --build

# Hoặc chạy ở background
docker-compose up -d

# Xem logs
docker-compose logs -f ai-service

# Stop services
docker-compose down
```

### 4. Chạy local (không dùng Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Root Endpoint
```bash
GET http://localhost:8000/
```

### Health Check
```bash
GET http://localhost:8000/health
```

### Generate Content
```bash
POST http://localhost:8000/ai/generate
Content-Type: application/json

{
  "message": "Tạo SRS cho hệ thống quản lý khách sạn"
}
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Response Formats

### SRS Response
```json
{
  "type": "srs",
  "response": {
    "title": "Hệ thống quản lý khách sạn",
    "functional_requirements": "...",
    "non_functional_requirements": "...",
    "detail": "# Software Requirements Specification\n\n..."
  }
}
```

### Wireframe Response
```json
{
  "type": "wireframe",
  "response": {
    "figma_link": "https://www.figma.com/file/.../auto-generated-wireframe",
    "editable": true,
    "description": "Giao diện đặt phòng, quản lý khách..."
  }
}
```

### Diagram Response
```json
{
  "type": "diagram",
  "response": {
    "figma_link": "https://www.figma.com/file/.../auto-generated-diagram",
    "editable": true,
    "description": "ERD gồm các bảng Room, Customer, Booking..."
  }
}
```

## Testing

### Test SRS Generation
```bash
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"message": "Tạo SRS cho hệ thống quản lý thư viện"}'
```

### Test Wireframe Generation
```bash
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"message": "Tạo wireframe cho trang đăng nhập và dashboard"}'
```

### Test Diagram Generation
```bash
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"message": "Tạo ERD cho hệ thống quản lý bán hàng"}'
```

## Project Structure

```
AI_Implement/
├── main.py                 # FastAPI application
├── ai_workflow.py          # LangGraph workflow
├── figma_mcp.py           # Figma integration
├── models/                 # Pydantic models
│   ├── __init__.py
│   ├── srs.py
│   ├── wireframe.py
│   └── diagram.py
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── .env                   # Environment variables (ignored)
├── .env.example          # Example environment file
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Architecture

```
User Request → FastAPI → LangGraph Workflow
                            ↓
                    Intent Classification (Gemini)
                            ↓
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
    SRS Node          Wireframe Node     Diagram Node
    (Gemini)          (Figma MCP)        (Gemini + Figma)
        ↓                  ↓                  ↓
    JSON Response     JSON Response      JSON Response
```

## Notes

- File `.env` chứa sensitive information và được ignore bởi git
- File `.env.example` chứa template cho environment variables
- Google API Key cần được cấu hình để sử dụng Gemini model
- Figma integration hiện tại là mock, có thể thay thế bằng real API

## Troubleshooting

### Docker build fails
```bash
# Clean up và rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Port already in use
```bash
# Đổi port trong docker-compose.yml
ports:
  - "8001:8000"  # Thay 8001 bằng port khác
```

### API Key không hoạt động
- Kiểm tra `.env` file có đúng format
- Verify API key tại Google AI Studio
- Restart container sau khi update `.env`
