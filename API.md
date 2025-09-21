# API Documentation - BA Copilot AI Services

**Mock API Endpoints for Testing and Development**

This document describes the 5 GET endpoints currently available in the BA Copilot AI Services. These endpoints return mock data and are designed for testing and development purposes.

## Base Information

- **Base URL**: `http://localhost:8000/v1`
- **Content Type**: `application/json`
- **Status**: Mock Implementation for Development/Testing

## Available Endpoints

### 1. Health Check

**Endpoint**: `GET /v1/health/`

**Description**: Returns the current health status of the API service and dependent components.

**URL**: `http://localhost:8000/v1/health/`

**Response (200 OK)**:

```json
{
  "status": "healthy",
  "timestamp": "2025-09-21T14:30:00Z",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "database": "healthy",
    "llm_providers": "healthy",
    "file_storage": "healthy",
    "cache": "healthy"
  },
  "uptime_seconds": 86400
}
```

**Error Codes**:

- `503 Service Unavailable` - Service unhealthy

**Ping Endpoint**: `GET /v1/health/ping`

**Response**: `{"message": "pong"}`

---

### 2. SRS Document Retrieval

**Endpoint**: `GET /v1/srs/{document_id}`

**Description**: Retrieves a Software Requirements Specification document by ID.

**URL**: `http://localhost:8000/v1/srs/{document_id}`

**Path Parameters**:

- `document_id` (string, required) - Document ID (must start with "doc\_")

**Example URL**: `http://localhost:8000/v1/srs/doc_550e8400-e29b-41d4-a716-446655440000`

**Response (200 OK)**:

```json
{
  "document_id": "doc_550e8400-e29b-41d4-a716-446655440000",
  "project_name": "E-commerce Platform",
  "content": "# Software Requirements Specification\n\n## 1. Introduction\n...",
  "metadata": {
    "created_at": "2025-09-20T14:30:00Z",
    "updated_at": "2025-09-20T14:30:00Z",
    "template_used": "standard",
    "status": "generated",
    "word_count": 150,
    "sections": 3
  }
}
```

**Error Codes**:

- `400 Bad Request` - Invalid document ID format

**Export Endpoint**: `GET /v1/srs/{document_id}/export`

**Query Parameters**:

- `format` (string, required) - Export format: `md`, `pdf`, `html`
- `include_metadata` (boolean, optional) - Include metadata (default: false)
- `include_diagrams` (boolean, optional) - Include diagrams (default: true)

**Example URL**: `http://localhost:8000/v1/srs/doc_550e8400/export?format=pdf&include_metadata=true`

**Response (200 OK)**:

```json
{
  "download_url": "http://localhost:8000/exports/doc_550e8400.pdf",
  "expires_at": "2025-09-21T14:30:00Z",
  "file_size_bytes": 245760,
  "format": "pdf"
}
```

---

### 3. Wireframe Retrieval

**Endpoint**: `GET /v1/wireframes/{wireframe_id}`

**Description**: Retrieves a generated wireframe with HTML, CSS, and component information.

**URL**: `http://localhost:8000/v1/wireframes/{wireframe_id}`

**Path Parameters**:

- `wireframe_id` (string, required) - Wireframe ID (must start with "wf\_")

**Example URL**: `http://localhost:8000/v1/wireframes/wf_550e8400-e29b-41d4-a716-446655440000`

**Response (200 OK)**:

```json
{
  "wireframe_id": "wf_550e8400-e29b-41d4-a716-446655440000",
  "preview_url": "http://localhost:8000/v1/wireframes/wf_550e8400/preview",
  "html_content": "<!DOCTYPE html>\n<html>...</html>",
  "css_styles": "/* Generated CSS styles */\n.dashboard-container { ... }",
  "components_identified": [
    {
      "type": "navigation",
      "properties": { "location": "sidebar", "items": 4 }
    },
    {
      "type": "header",
      "properties": { "title": "Dashboard", "has_user_profile": true }
    }
  ],
  "metadata": {
    "template_used": "dashboard",
    "responsive_breakpoints": ["768px", "1024px", "1200px"],
    "created_at": "2025-09-20T14:30:00Z",
    "updated_at": "2025-09-20T14:30:00Z",
    "status": "generated",
    "target_devices": ["desktop", "tablet", "mobile"]
  }
}
```

**Error Codes**:

- `400 Bad Request` - Invalid wireframe ID format

**Export Endpoint**: `GET /v1/wireframes/{wireframe_id}/export`

**Query Parameters**:

- `format` (string, required) - Export format: `html`, `zip`, `figma`
- `include_css` (boolean, optional) - Include CSS files (default: true)
- `responsive` (boolean, optional) - Include responsive design (default: true)

**Example URL**: `http://localhost:8000/v1/wireframes/wf_550e8400/export?format=zip&include_css=true`

---

### 4. Diagram Retrieval

**Endpoint**: `GET /v1/diagrams/{diagram_id}`

**Description**: Retrieves a generated diagram with Mermaid code and metadata.

**URL**: `http://localhost:8000/v1/diagrams/{diagram_id}`

**Path Parameters**:

- `diagram_id` (string, required) - Diagram ID (must start with "diag\_")

**Example URL**: `http://localhost:8000/v1/diagrams/diag_550e8400-seq-001`

**Response (200 OK)**:

```json
{
  "diagram_id": "diag_550e8400-seq-001",
  "type": "sequence",
  "title": "User Authentication Flow",
  "mermaid_code": "sequenceDiagram\n    participant U as User\n    participant F as Frontend\n...",
  "preview_url": "http://localhost:8000/v1/diagrams/diag_550e8400-seq-001/preview",
  "metadata": {
    "created_at": "2025-09-20T14:30:00Z",
    "updated_at": "2025-09-20T14:30:00Z",
    "status": "generated",
    "complexity": "medium",
    "actors_count": 5,
    "interactions_count": 8
  }
}
```

**Error Codes**:

- `400 Bad Request` - Invalid diagram ID format

**Export Endpoint**: `GET /v1/diagrams/{diagram_id}/export`

**Query Parameters**:

- `format` (string, required) - Export format: `svg`, `png`, `pdf`, `mermaid`
- `quality` (string, optional) - Image quality: `low`, `medium`, `high` (default: medium)
- `theme` (string, optional) - Diagram theme: `default`, `dark`, `forest`, `neutral` (default: default)

**Example URL**: `http://localhost:8000/v1/diagrams/diag_550e8400/export?format=png&quality=high&theme=dark`

**List Diagrams**: `GET /v1/diagrams/`

**Query Parameters**:

- `type` (string, optional) - Filter by type: `sequence`, `architecture`, `usecase`, `flowchart`
- `limit` (integer, optional) - Maximum results (1-100, default: 20)
- `offset` (integer, optional) - Pagination offset (default: 0)
- `search` (string, optional) - Search in diagram titles

**Example URL**: `http://localhost:8000/v1/diagrams/?type=sequence&limit=10&search=authentication`

---

### 5. Conversation Retrieval

**Endpoint**: `GET /v1/conversations/{conversation_id}`

**Description**: Retrieves a conversation with complete message history and metadata.

**URL**: `http://localhost:8000/v1/conversations/{conversation_id}`

**Path Parameters**:

- `conversation_id` (string, required) - Conversation ID (must start with "conv\_")

**Example URL**: `http://localhost:8000/v1/conversations/conv_550e8400-001`

**Response (200 OK)**:

```json
{
  "conversation_id": "conv_550e8400-001",
  "title": "E-commerce SRS Development Discussion",
  "messages": [
    {
      "message_id": "msg_001",
      "role": "user",
      "content": "I need help creating an SRS document...",
      "timestamp": "2025-09-20T14:30:00Z",
      "metadata": { "word_count": 18 }
    },
    {
      "message_id": "msg_002",
      "role": "assistant",
      "content": "I'd be happy to help you create an SRS document...",
      "timestamp": "2025-09-20T14:30:15Z",
      "metadata": { "word_count": 87, "response_time_ms": 1250 }
    }
  ],
  "metadata": {
    "project_type": "e-commerce",
    "domain": "electronics",
    "llm_provider": "openai",
    "total_messages": 4,
    "user_messages": 2,
    "assistant_messages": 2,
    "average_response_time_ms": 1525,
    "conversation_status": "active",
    "last_activity": "2025-09-20T14:32:45Z"
  },
  "created_at": "2025-09-20T14:30:00Z",
  "updated_at": "2025-09-20T14:32:45Z"
}
```

**Error Codes**:

- `400 Bad Request` - Invalid conversation ID format

**List Conversations**: `GET /v1/conversations/`

**Query Parameters**:

- `limit` (integer, optional) - Maximum results (1-100, default: 20)
- `offset` (integer, optional) - Pagination offset (default: 0)
- `search` (string, optional) - Search in conversation titles and previews
- `status` (string, optional) - Filter by status: `active`, `archived`, `completed`

**Example URL**: `http://localhost:8000/v1/conversations/?status=active&limit=10&search=SRS`

---

## Common Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid document ID format"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### 503 Service Unavailable

```json
{
  "detail": "Service unhealthy: Database connection failed"
}
```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/v1/health/

# Get SRS document
curl http://localhost:8000/v1/srs/doc_550e8400-e29b-41d4-a716-446655440000

# List diagrams with filters
curl "http://localhost:8000/v1/diagrams/?type=sequence&limit=5"

# Export wireframe
curl "http://localhost:8000/v1/wireframes/wf_550e8400/export?format=html"
```

### Using Python requests

```python
import requests

base_url = "http://localhost:8000/v1"

# Health check
response = requests.get(f"{base_url}/health/")
print(response.json())

# Get conversation
conv_id = "conv_550e8400-001"
response = requests.get(f"{base_url}/conversations/{conv_id}")
print(response.json())
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Notes

- **Mock Data**: All endpoints return predefined mock data
- **ID Formats**: Each resource type has a specific ID prefix requirement
- **Pagination**: List endpoints support offset-based pagination
- **Query Parameters**: All query parameters are validated according to API specs
- **Error Handling**: Comprehensive error messages with appropriate HTTP status codes
- **CORS Enabled**: Cross-origin requests are supported for frontend integration

## Development Status

✅ **Implemented**:

- All 5 GET endpoints with mock data
- Comprehensive test coverage
- Docker containerization
- API documentation
- Error handling

🔄 **Future Enhancements**:

- Real AI integration
- Database persistence
- Authentication system
- Rate limiting
- File upload support
