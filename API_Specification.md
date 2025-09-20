# API Specification - BA Copilot AI Core Services

## Overview

This document specifies the RESTful API endpoints for the BA Copilot AI Core Services backend. The API follows industry standards and best practices for REST services, providing comprehensive AI-powered tools for Business Analysts.

**Base URL**: `https://api.bacopilot.com/v1`  
**API Version**: 1.0  
**Protocol**: HTTPS only  
**Content-Type**: `application/json`

## Authentication

All API endpoints require authentication using JWT Bearer tokens.

### Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
Accept: application/json
```

### Authentication Endpoints

#### POST /auth/register

Register a new user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "organization": "TechCorp Inc."
}
```

**Response (201 Created):**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-10-20T14:30:00Z",
  "created_at": "2025-09-20T14:30:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid input data
- `409 Conflict`: Email already exists
- `422 Unprocessable Entity`: Password requirements not met

#### POST /auth/login

Authenticate user and receive access token.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-09-20T18:30:00Z",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

**Error Responses:**

- `400 Bad Request`: Missing email or password
- `401 Unauthorized`: Invalid credentials
- `429 Too Many Requests`: Rate limit exceeded

#### POST /auth/refresh

Refresh an expired access token.

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-09-20T18:30:00Z"
}
```

## SRS Generator Service

### POST /srs/generate

Generate Software Requirements Specification document from user input.

**Request Body:**

```json
{
  "project_name": "E-commerce Platform",
  "overview": "A comprehensive e-commerce platform with user management, product catalog, and payment processing",
  "features": [
    "User authentication and registration",
    "Product catalog with search and filtering",
    "Shopping cart and checkout process",
    "Payment gateway integration",
    "Admin dashboard for inventory management"
  ],
  "additional_requirements": "The system should support multiple languages and currencies",
  "template_type": "standard",
  "include_diagrams": true
}
```

**Response (200 OK):**

```json
{
  "document_id": "doc_550e8400-e29b-41d4-a716-446655440000",
  "project_name": "E-commerce Platform",
  "content": "# Software Requirements Specification\n\n## 1. Introduction...",
  "metadata": {
    "template_used": "standard",
    "sections_generated": [
      "introduction",
      "overall_description",
      "system_features",
      "external_interfaces",
      "non_functional_requirements"
    ],
    "word_count": 2547,
    "generated_at": "2025-09-20T14:30:00Z",
    "processing_time_ms": 3420
  },
  "export_urls": {
    "markdown": "https://api.bacopilot.com/v1/srs/doc_550e8400/export?format=md",
    "pdf": "https://api.bacopilot.com/v1/srs/doc_550e8400/export?format=pdf",
    "html": "https://api.bacopilot.com/v1/srs/doc_550e8400/export?format=html"
  }
}
```

**Error Responses:**

- `400 Bad Request`: Invalid or missing required fields
- `401 Unauthorized`: Authentication required
- `413 Payload Too Large`: Input content exceeds size limit
- `422 Unprocessable Entity`: Unable to process requirements
- `503 Service Unavailable`: LLM service temporarily unavailable

### GET /srs/{document_id}

Retrieve a previously generated SRS document.

**Path Parameters:**

- `document_id` (string, required): Unique document identifier

**Response (200 OK):**

```json
{
  "document_id": "doc_550e8400-e29b-41d4-a716-446655440000",
  "project_name": "E-commerce Platform",
  "content": "# Software Requirements Specification\n\n## 1. Introduction...",
  "metadata": {
    "created_at": "2025-09-20T14:30:00Z",
    "updated_at": "2025-09-20T14:30:00Z",
    "version": "1.0",
    "status": "generated"
  }
}
```

**Error Responses:**

- `404 Not Found`: Document not found or access denied
- `410 Gone`: Document has been deleted

### PUT /srs/{document_id}

Update an existing SRS document.

**Request Body:**

```json
{
  "content": "# Updated Software Requirements Specification\n\n## 1. Introduction...",
  "change_summary": "Updated system requirements and added new features"
}
```

**Response (200 OK):**

```json
{
  "document_id": "doc_550e8400-e29b-41d4-a716-446655440000",
  "content": "# Updated Software Requirements Specification...",
  "metadata": {
    "updated_at": "2025-09-20T15:45:00Z",
    "version": "1.1",
    "change_summary": "Updated system requirements and added new features"
  }
}
```

### GET /srs/{document_id}/export

Export SRS document in specified format.

**Query Parameters:**

- `format` (string, required): Export format (`md`, `pdf`, `html`, `docx`)
- `include_metadata` (boolean, optional): Include metadata in export (default: false)

**Response (200 OK):**

```json
{
  "download_url": "https://storage.bacopilot.com/exports/doc_550e8400.pdf",
  "expires_at": "2025-09-21T14:30:00Z",
  "file_size_bytes": 245760,
  "format": "pdf"
}
```

## Wireframe Generator Service

### POST /wireframe/generate

Generate wireframe prototypes from textual requirements.

**Request Body:**

```json
{
  "page_description": "A user dashboard with navigation sidebar, main content area showing analytics charts, and user profile section",
  "template": "dashboard",
  "style_preferences": {
    "color_scheme": "light",
    "component_style": "modern",
    "responsive": true
  },
  "target_devices": ["desktop", "tablet"],
  "interactive_elements": true
}
```

**Response (201 Created):**

```json
{
  "wireframe_id": "wf_550e8400-e29b-41d4-a716-446655440000",
  "preview_url": "https://preview.bacopilot.com/wireframes/wf_550e8400",
  "html_content": "<!DOCTYPE html>\n<html>...",
  "css_styles": "/* Generated CSS styles */\n.dashboard-container { ... }",
  "components_identified": [
    {
      "type": "sidebar",
      "position": "left",
      "items": ["navigation", "user_menu"]
    },
    {
      "type": "main_content",
      "position": "center",
      "items": ["analytics_charts", "data_tables"]
    },
    {
      "type": "profile_section",
      "position": "top-right",
      "items": ["avatar", "settings_dropdown"]
    }
  ],
  "metadata": {
    "template_used": "dashboard",
    "generated_at": "2025-09-20T14:30:00Z",
    "processing_time_ms": 2100,
    "responsive_breakpoints": ["768px", "1024px", "1200px"]
  }
}
```

**Error Responses:**

- `400 Bad Request`: Invalid page description or template
- `401 Unauthorized`: Authentication required
- `422 Unprocessable Entity`: Unable to parse requirements
- `503 Service Unavailable`: Wireframe generation service unavailable

### GET /wireframe/{wireframe_id}

Retrieve a generated wireframe.

**Path Parameters:**

- `wireframe_id` (string, required): Unique wireframe identifier

**Response (200 OK):**

```json
{
  "wireframe_id": "wf_550e8400-e29b-41d4-a716-446655440000",
  "preview_url": "https://preview.bacopilot.com/wireframes/wf_550e8400",
  "html_content": "<!DOCTYPE html>\n<html>...",
  "css_styles": "/* Generated CSS styles */",
  "metadata": {
    "created_at": "2025-09-20T14:30:00Z",
    "template": "dashboard",
    "status": "generated"
  }
}
```

### PUT /wireframe/{wireframe_id}

Update an existing wireframe.

**Request Body:**

```json
{
  "html_content": "<!DOCTYPE html>\n<html>...",
  "css_styles": "/* Updated CSS styles */",
  "change_summary": "Modified navigation layout and added responsive features"
}
```

**Response (200 OK):**

```json
{
  "wireframe_id": "wf_550e8400-e29b-41d4-a716-446655440000",
  "preview_url": "https://preview.bacopilot.com/wireframes/wf_550e8400",
  "html_content": "<!DOCTYPE html>\n<html>...",
  "metadata": {
    "updated_at": "2025-09-20T15:45:00Z",
    "version": "1.1"
  }
}
```

### GET /wireframe/{wireframe_id}/export

Export wireframe in specified format.

**Query Parameters:**

- `format` (string, required): Export format (`html`, `figma`, `sketch`, `pdf`)
- `include_assets` (boolean, optional): Include CSS and JS files (default: true)

**Response (200 OK):**

```json
{
  "download_url": "https://storage.bacopilot.com/wireframes/wf_550e8400.zip",
  "expires_at": "2025-09-21T14:30:00Z",
  "format": "html",
  "files_included": ["index.html", "styles.css", "script.js", "assets/"]
}
```

## AI Conversation Service

### POST /conversations

Create a new conversation session.

**Request Body:**

```json
{
  "title": "Project Requirements Discussion",
  "context": "Discussion about e-commerce platform requirements",
  "conversation_type": "requirements_analysis",
  "metadata": {
    "project_id": "proj_123",
    "tags": ["ecommerce", "requirements", "planning"]
  }
}
```

**Response (201 Created):**

```json
{
  "conversation_id": "conv_550e8400-e29b-41d4-a716-446655440000",
  "title": "Project Requirements Discussion",
  "created_at": "2025-09-20T14:30:00Z",
  "session_token": "sess_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "websocket_url": "wss://api.bacopilot.com/v1/conversations/conv_550e8400/ws"
}
```

### POST /conversations/{conversation_id}/messages

Send a message in a conversation.

**Path Parameters:**

- `conversation_id` (string, required): Unique conversation identifier

**Request Body:**

```json
{
  "message": "What are the key requirements for user authentication in an e-commerce platform?",
  "message_type": "text",
  "attachments": [
    {
      "type": "document",
      "filename": "requirements_draft.md",
      "content": "base64_encoded_content",
      "size_bytes": 2048
    }
  ],
  "context_preferences": {
    "include_previous_messages": 5,
    "focus_area": "technical_requirements"
  }
}
```

**Response (200 OK):**

```json
{
  "message_id": "msg_550e8400-e29b-41d4-a716-446655440000",
  "conversation_id": "conv_550e8400-e29b-41d4-a716-446655440000",
  "user_message": {
    "content": "What are the key requirements for user authentication in an e-commerce platform?",
    "timestamp": "2025-09-20T14:30:00Z",
    "message_id": "msg_user_550e8400"
  },
  "ai_response": {
    "content": "For user authentication in an e-commerce platform, here are the key requirements:\n\n1. **Multi-factor Authentication (MFA)**...",
    "timestamp": "2025-09-20T14:30:15Z",
    "message_id": "msg_ai_550e8400",
    "processing_time_ms": 1500,
    "confidence_score": 0.95,
    "sources_used": ["security_best_practices", "ecommerce_standards"]
  },
  "conversation_metadata": {
    "total_messages": 12,
    "last_activity": "2025-09-20T14:30:15Z"
  }
}
```

### GET /conversations/{conversation_id}

Retrieve conversation history.

**Path Parameters:**

- `conversation_id` (string, required): Unique conversation identifier

**Query Parameters:**

- `limit` (integer, optional): Maximum messages to return (default: 50, max: 100)
- `offset` (integer, optional): Message offset for pagination (default: 0)
- `include_metadata` (boolean, optional): Include message metadata (default: false)

**Response (200 OK):**

```json
{
  "conversation_id": "conv_550e8400-e29b-41d4-a716-446655440000",
  "title": "Project Requirements Discussion",
  "created_at": "2025-09-20T14:00:00Z",
  "updated_at": "2025-09-20T14:30:15Z",
  "message_count": 12,
  "messages": [
    {
      "message_id": "msg_550e8400-1",
      "role": "user",
      "content": "What are the key requirements for user authentication?",
      "timestamp": "2025-09-20T14:30:00Z",
      "attachments": []
    },
    {
      "message_id": "msg_550e8400-2",
      "role": "assistant",
      "content": "For user authentication in an e-commerce platform...",
      "timestamp": "2025-09-20T14:30:15Z",
      "metadata": {
        "processing_time_ms": 1500,
        "model_used": "gpt-4",
        "confidence_score": 0.95
      }
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "has_more": false
  }
}
```

### DELETE /conversations/{conversation_id}

Delete a conversation and its history.

**Path Parameters:**

- `conversation_id` (string, required): Unique conversation identifier

**Response (204 No Content)**

### GET /conversations

List user's conversations.

**Query Parameters:**

- `limit` (integer, optional): Maximum conversations to return (default: 20, max: 50)
- `offset` (integer, optional): Pagination offset (default: 0)
- `search` (string, optional): Search in conversation titles and content
- `tag` (string, optional): Filter by tag
- `created_after` (string, optional): ISO datetime filter
- `created_before` (string, optional): ISO datetime filter

**Response (200 OK):**

```json
{
  "conversations": [
    {
      "conversation_id": "conv_550e8400",
      "title": "Project Requirements Discussion",
      "created_at": "2025-09-20T14:00:00Z",
      "updated_at": "2025-09-20T14:30:15Z",
      "message_count": 12,
      "preview": "What are the key requirements for user authentication...",
      "tags": ["ecommerce", "requirements", "planning"]
    }
  ],
  "pagination": {
    "total_count": 25,
    "current_page": 1,
    "total_pages": 2,
    "has_more": true
  }
}
```

### GET /conversations/{conversation_id}/export

Export conversation transcript.

**Query Parameters:**

- `format` (string, required): Export format (`md`, `pdf`, `txt`, `json`)
- `include_metadata` (boolean, optional): Include message metadata (default: false)

**Response (200 OK):**

```json
{
  "download_url": "https://storage.bacopilot.com/transcripts/conv_550e8400.pdf",
  "expires_at": "2025-09-21T14:30:00Z",
  "format": "pdf",
  "file_size_bytes": 156789
}
```

## User Management

### GET /users/me

Get current user profile.

**Response (200 OK):**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "organization": "TechCorp Inc.",
  "created_at": "2025-08-15T10:30:00Z",
  "preferences": {
    "default_srs_template": "standard",
    "default_wireframe_style": "modern",
    "ai_response_length": "detailed",
    "notification_settings": {
      "email_notifications": true,
      "export_completion": true
    }
  },
  "usage_stats": {
    "srs_generated": 15,
    "wireframes_created": 8,
    "conversations_started": 23,
    "api_calls_this_month": 156
  }
}
```

### PUT /users/me

Update user profile.

**Request Body:**

```json
{
  "full_name": "John Smith",
  "organization": "NewTech Corp",
  "preferences": {
    "default_srs_template": "agile",
    "ai_response_length": "concise"
  }
}
```

**Response (200 OK):**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Smith",
  "organization": "NewTech Corp",
  "updated_at": "2025-09-20T14:30:00Z"
}
```

## Error Handling

All API endpoints use standard HTTP status codes and return consistent error responses:

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid parameters",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "request_id": "req_550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-09-20T14:30:00Z"
  }
}
```

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no content returned
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Authentication required or invalid
- **403 Forbidden**: Access denied to resource
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict (e.g., duplicate email)
- **413 Payload Too Large**: Request body exceeds size limit
- **422 Unprocessable Entity**: Request valid but cannot be processed
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Service temporarily unavailable

## Rate Limiting

API requests are rate limited per user:

- **Authentication**: 10 requests per minute
- **SRS Generation**: 5 requests per minute
- **Wireframe Generation**: 3 requests per minute
- **AI Conversations**: 60 requests per minute
- **General API**: 100 requests per minute

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1695220800
```

## Webhooks (Optional)

For real-time updates on long-running operations:

### Webhook Events

- `srs.generation.completed`
- `srs.generation.failed`
- `wireframe.generation.completed`
- `wireframe.generation.failed`
- `conversation.message.received`

### Webhook Payload

```json
{
  "event": "srs.generation.completed",
  "data": {
    "document_id": "doc_550e8400",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "metadata": {
      "processing_time_ms": 3420,
      "word_count": 2547
    }
  },
  "timestamp": "2025-09-20T14:30:00Z"
}
```

## API Versioning

The API uses URL-based versioning. Current version is v1. When breaking changes are introduced, a new version will be released with backward compatibility maintained for previous versions for at least 12 months.

## SDK and Libraries

Official SDKs are available for:

- Python (`bacopilot-python`)
- Node.js (`bacopilot-node`)
- JavaScript/TypeScript (`bacopilot-js`)

Example usage:

```python
from bacopilot import Client

client = Client(api_key="your_api_key")
srs = client.srs.generate(
    project_name="My Project",
    features=["Authentication", "Dashboard"]
)
```
