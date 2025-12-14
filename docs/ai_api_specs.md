# AI API Specification - BA Copilot AI Services

This document specifies the AI-powered REST API endpoints provided by the BA Copilot AI Services backend. This is one of three repositories in the BA Copilot ecosystem, specifically handling AI-powered document and diagram generation services.

**Repository Context**: This is the **AI Services Repository** - one of three repositories:

1. **Frontend Repository**: NextJS + ReactJS + TailwindCSS
2. **Backend Repository**: Core business logic, user management, and database operations
3. **AI Services Repository** (This repo): AI-powered generation services

**Base URL**: `http://localhost:8000/v1` (Development)  
**API Version**: 1.0  
**Content-Type**: `application/json`

## Authentication & User Management

**Important**: This AI Services repository does **NOT** handle user authentication or user management. All authentication is handled by the **Backend Repository**.

### Authentication Flow

1. **User Authentication**: Users authenticate through the Backend Repository
2. **JWT Token**: Backend provides JWT tokens containing `user_id` and other claims
3. **AI Service Requests**: Frontend sends requests to AI Services with JWT token
4. **User Context**: AI Services extract `user_id` from JWT for data association

### Required Headers

All AI service endpoints require JWT Bearer token authentication provided by the Backend Repository.

```http
Authorization: Bearer <jwt_token_from_backend>
Content-Type: application/json
Accept: application/json
```

### User Data Handling

- **No User Table**: AI Services DB does NOT contain a `users` table
- **User ID Only**: AI Services store only `user_id` (UUID) from JWT claims
- **No Foreign Keys**: No foreign key constraints to non-existent `users` table
- **Application-Level Joins**: User information joined at application layer, not SQL level

````

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
    "Payment integration with multiple providers",
    "Order management and tracking",
    "Admin dashboard for inventory management"
  ],
  "additional_requirements": "The system should support multiple languages and currencies",
  "template_type": "standard",
  "include_diagrams": true,
  "diagram_types": ["sequence", "architecture", "use_case"]
}
````

**Response (200 OK):**

```json
{
  "document_id": "doc_550e8400-e29b-41d4-a716-446655440000",
  "project_name": "E-commerce Platform",
  "content": "# Software Requirements Specification\n\n## 1. Introduction...",
  "metadata": {
    "template_used": "standard",
    "word_count": 2340,
    "sections_generated": 12,
    "diagrams_included": true,
    "diagram_count": 3,
    "processing_time_ms": 3420
  },
  "export_urls": {
    "markdown": "http://localhost:8000/v1/srs/doc_550e8400/export?format=md",
    "pdf": "http://localhost:8000/v1/srs/doc_550e8400/export?format=pdf",
    "html": "http://localhost:8000/v1/srs/doc_550e8400/export?format=html"
  },
  "diagrams": [
    {
      "diagram_id": "diag_550e8400-seq-001",
      "type": "sequence",
      "title": "User Authentication Sequence",
      "mermaid_code": "sequenceDiagram...",
      "preview_url": "http://localhost:8000/v1/diagrams/diag_550e8400-seq-001/preview"
    }
  ]
}
```

### GET /srs/{document_id}

Retrieve a previously generated SRS document.

**Response (200 OK):**

```json
{
  "document_id": "doc_550e8400-e29b-41d4-a716-446655440000",
  "project_name": "E-commerce Platform",
  "content": "# Software Requirements Specification\n\n## 1. Introduction...",
  "metadata": {
    "created_at": "2025-09-20T14:30:00Z",
    "updated_at": "2025-09-20T14:30:00Z",
    "template_used": "standard",
    "status": "generated"
  }
}
```

### PUT /srs/{document_id}

Update an existing SRS document.

**Request Body:**

```json
{
  "content": "# Updated Software Requirements Specification\n\n## 1. Introduction...",
  "change_summary": "Updated system requirements and added new features"
}
```

### GET /srs/{document_id}/export

Export SRS document in specified format.

**Query Parameters:**

- `format` (string, required): Export format (`md`, `pdf`, `html`)
- `include_metadata` (boolean, optional): Include metadata in export (default: false)
- `include_diagrams` (boolean, optional): Include generated diagrams (default: true)

**Response (200 OK):**

```json
{
  "download_url": "http://localhost:8000/exports/doc_550e8400.pdf",
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
    "layout": "sidebar",
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
  "preview_url": "http://localhost:8000/wireframes/wf_550e8400/preview",
  "html_content": "<!DOCTYPE html>\n<html>...",
  "css_styles": "/* Generated CSS styles */\n.dashboard-container { ... }",
  "components_identified": [
    {
      "type": "navigation",
      "position": "left-sidebar",
      "items": ["Dashboard", "Analytics", "Settings"]
    }
  ],
  "metadata": {
    "template_used": "dashboard",
    "responsive_breakpoints": ["768px", "1024px", "1200px"]
  }
}
```

### GET /wireframe/{wireframe_id}

Retrieve a generated wireframe.

### PUT /wireframe/{wireframe_id}

Update an existing wireframe.

### GET /wireframe/{wireframe_id}/export

Export wireframe in specified format.

## AI Conversation Service

### POST /conversations

Create a new conversation session.

**Request Body:**

```json
{
  "title": "Project Requirements Discussion",
  "context": {
    "project_type": "web_application",
    "domain": "e-commerce",
    "preferred_llm": "openai"
  }
}
```

**Response (201 Created):**

```json
{
  "conversation_id": "conv_550e8400-e29b-41d4-a716-446655440000",
  "title": "Project Requirements Discussion",
  "created_at": "2025-09-20T14:30:00Z",
  "websocket_url": "ws://localhost:8000/v1/conversations/conv_550e8400/ws"
}
```

### POST /conversations/{conversation_id}/messages

Send a message in a conversation.

### GET /conversations/{conversation_id}

Retrieve conversation history.

### DELETE /conversations/{conversation_id}

Delete a conversation and its history.

### GET /conversations

List user's conversations.

## Diagram Generator Service

### POST /diagrams/sequence/generate

Generate sequence diagrams from requirements or existing SRS documents.

**Request Body:**

```json
{
  "title": "User Authentication Flow",
  "description": "Generate a sequence diagram showing the user authentication process including login, token validation, and session management",
  "actors": ["User", "Frontend", "Backend", "Database", "Auth Service"],
  "interactions": [
    {
      "from": "User",
      "to": "Frontend",
      "action": "Enter credentials",
      "type": "sync"
    },
    {
      "from": "Frontend",
      "to": "Backend",
      "action": "POST /auth/login",
      "type": "async"
    },
    {
      "from": "Backend",
      "to": "Database",
      "action": "Validate user",
      "type": "sync"
    }
  ],
  "style_preferences": {
    "theme": "default",
    "actor_style": "box",
    "sequence_numbering": true
  }
}
```

**Response (201 Created):**

```json
{
  "diagram_id": "diag_550e8400-seq-001",
  "type": "sequence",
  "title": "User Authentication Flow",
  "mermaid_code": "sequenceDiagram\n    participant U as User\n    participant F as Frontend\n    participant B as Backend\n    participant D as Database\n    participant A as Auth Service\n    \n    U->>F: Enter credentials\n    F->>+B: POST /auth/login\n    B->>+D: Validate user\n    D-->>-B: User data\n    B->>+A: Generate token\n    A-->>-B: JWT token\n    B-->>-F: Authentication response\n    F-->>U: Login success",
  "preview_url": "http://localhost:8000/v1/diagrams/diag_550e8400-seq-001/preview",
  "export_urls": {
    "svg": "http://localhost:8000/v1/diagrams/diag_550e8400-seq-001/export?format=svg",
    "png": "http://localhost:8000/v1/diagrams/diag_550e8400-seq-001/export?format=png",
    "pdf": "http://localhost:8000/v1/diagrams/diag_550e8400-seq-001/export?format=pdf",
    "mermaid": "http://localhost:8000/v1/diagrams/diag_550e8400-seq-001/export?format=mermaid"
  },
  "metadata": {
    "actors_count": 5,
    "interactions_count": 7,
    "generated_at": "2025-09-20T14:30:00Z",
    "processing_time_ms": 1250,
    "llm_used": "openai-gpt-4"
  }
}
```

### POST /diagrams/architecture/generate

Generate system architecture diagrams from high-level descriptions.

**Request Body:**

```json
{
  "title": "E-commerce System Architecture",
  "description": "Generate an architecture diagram for a scalable e-commerce platform with microservices, databases, and external integrations",
  "components": [
    {
      "name": "Web Frontend",
      "type": "client",
      "technology": "React"
    },
    {
      "name": "API Gateway",
      "type": "service",
      "technology": "Kong"
    },
    {
      "name": "User Service",
      "type": "service",
      "technology": "Node.js"
    },
    {
      "name": "Product Service",
      "type": "service",
      "technology": "Python"
    },
    {
      "name": "PostgreSQL",
      "type": "database",
      "technology": "PostgreSQL"
    }
  ],
  "connections": [
    {
      "from": "Web Frontend",
      "to": "API Gateway",
      "type": "http"
    },
    {
      "from": "API Gateway",
      "to": "User Service",
      "type": "http"
    }
  ],
  "style_preferences": {
    "layout": "top-down",
    "grouping": "by_layer",
    "show_technologies": true
  }
}
```

**Response (201 Created):**

```json
{
  "diagram_id": "diag_550e8400-arch-001",
  "type": "architecture",
  "title": "E-commerce System Architecture",
  "mermaid_code": "graph TD\n    subgraph \"Client Layer\"\n        WF[Web Frontend - React]\n    end\n    \n    subgraph \"API Layer\"\n        GW[API Gateway - Kong]\n    end\n    \n    subgraph \"Service Layer\"\n        US[User Service - Node.js]\n        PS[Product Service - Python]\n    end\n    \n    subgraph \"Data Layer\"\n        PG[(PostgreSQL)]\n    end\n    \n    WF --> GW\n    GW --> US\n    GW --> PS\n    US --> PG\n    PS --> PG",
  "preview_url": "http://localhost:8000/v1/diagrams/diag_550e8400-arch-001/preview",
  "export_urls": {
    "svg": "http://localhost:8000/v1/diagrams/diag_550e8400-arch-001/export?format=svg",
    "png": "http://localhost:8000/v1/diagrams/diag_550e8400-arch-001/export?format=png",
    "pdf": "http://localhost:8000/v1/diagrams/diag_550e8400-arch-001/export?format=pdf",
    "mermaid": "http://localhost:8000/v1/diagrams/diag_550e8400-arch-001/export?format=mermaid"
  },
  "metadata": {
    "components_count": 5,
    "connections_count": 5,
    "layers_identified": 4,
    "generated_at": "2025-09-20T14:30:00Z",
    "processing_time_ms": 1800,
    "llm_used": "openai-gpt-4"
  }
}
```

### POST /diagrams/usecase/generate

Generate use case diagrams from user stories or requirements.

**Request Body:**

```json
{
  "title": "E-commerce Use Cases",
  "description": "Generate use case diagrams for an e-commerce platform showing user interactions",
  "actors": [
    {
      "name": "Customer",
      "type": "primary",
      "description": "End user purchasing products"
    },
    {
      "name": "Admin",
      "type": "primary",
      "description": "System administrator"
    },
    {
      "name": "Payment Gateway",
      "type": "external",
      "description": "External payment processing system"
    }
  ],
  "use_cases": [
    {
      "name": "Browse Products",
      "description": "Customer can browse product catalog",
      "actor": "Customer",
      "type": "primary"
    },
    {
      "name": "Add to Cart",
      "description": "Customer can add products to shopping cart",
      "actor": "Customer",
      "type": "primary"
    },
    {
      "name": "Process Payment",
      "description": "System processes payment through external gateway",
      "actor": "Customer",
      "includes": ["Validate Payment"],
      "extends": []
    },
    {
      "name": "Manage Inventory",
      "description": "Admin can manage product inventory",
      "actor": "Admin",
      "type": "primary"
    }
  ],
  "relationships": [
    {
      "type": "include",
      "from": "Process Payment",
      "to": "Validate Payment"
    }
  ],
  "style_preferences": {
    "show_actor_types": true,
    "group_by_actor": false,
    "show_relationships": true
  }
}
```

**Response (201 Created):**

```json
{
  "diagram_id": "diag_550e8400-uc-001",
  "type": "usecase",
  "title": "E-commerce Use Cases",
  "mermaid_code": "graph TB\n    subgraph \"E-commerce System\"\n        UC1[Browse Products]\n        UC2[Add to Cart]\n        UC3[Process Payment]\n        UC4[Validate Payment]\n        UC5[Manage Inventory]\n    end\n    \n    Customer --> UC1\n    Customer --> UC2\n    Customer --> UC3\n    Admin --> UC5\n    UC3 -.->|includes| UC4\n    UC3 --> PaymentGW[Payment Gateway]",
  "preview_url": "http://localhost:8000/v1/diagrams/diag_550e8400-uc-001/preview",
  "export_urls": {
    "svg": "http://localhost:8000/v1/diagrams/diag_550e8400-uc-001/export?format=svg",
    "png": "http://localhost:8000/v1/diagrams/diag_550e8400-uc-001/export?format=png",
    "pdf": "http://localhost:8000/v1/diagrams/diag_550e8400-uc-001/export?format=pdf",
    "mermaid": "http://localhost:8000/v1/diagrams/diag_550e8400-uc-001/export?format=mermaid"
  },
  "metadata": {
    "actors_count": 3,
    "use_cases_count": 5,
    "relationships_count": 1,
    "generated_at": "2025-09-20T14:30:00Z",
    "processing_time_ms": 2100,
    "llm_used": "claude-3"
  }
}
```

### POST /diagrams/flowchart/generate

Generate flowcharts from process descriptions.

**Request Body:**

```json
{
  "title": "Order Processing Workflow",
  "description": "Generate a flowchart showing the order processing workflow from order placement to delivery",
  "process_steps": [
    {
      "id": "start",
      "type": "start",
      "label": "Order Placed",
      "description": "Customer places an order"
    },
    {
      "id": "validate",
      "type": "process",
      "label": "Validate Order",
      "description": "Check product availability and customer details"
    },
    {
      "id": "payment_check",
      "type": "decision",
      "label": "Payment Valid?",
      "description": "Check if payment is successful"
    },
    {
      "id": "process_order",
      "type": "process",
      "label": "Process Order",
      "description": "Generate invoice and prepare for shipping"
    },
    {
      "id": "payment_failed",
      "type": "process",
      "label": "Payment Failed",
      "description": "Notify customer and cancel order"
    },
    {
      "id": "end_success",
      "type": "end",
      "label": "Order Complete"
    },
    {
      "id": "end_failure",
      "type": "end",
      "label": "Order Cancelled"
    }
  ],
  "connections": [
    {
      "from": "start",
      "to": "validate"
    },
    {
      "from": "validate",
      "to": "payment_check"
    },
    {
      "from": "payment_check",
      "to": "process_order",
      "condition": "Yes"
    },
    {
      "from": "payment_check",
      "to": "payment_failed",
      "condition": "No"
    },
    {
      "from": "process_order",
      "to": "end_success"
    },
    {
      "from": "payment_failed",
      "to": "end_failure"
    }
  ],
  "style_preferences": {
    "direction": "top-down",
    "show_conditions": true,
    "decision_style": "diamond"
  }
}
```

**Response (201 Created):**

```json
{
  "diagram_id": "diag_550e8400-flow-001",
  "type": "flowchart",
  "title": "Order Processing Workflow",
  "mermaid_code": "flowchart TD\n    A([Order Placed]) --> B[Validate Order]\n    B --> C{Payment Valid?}\n    C -->|Yes| D[Process Order]\n    C -->|No| E[Payment Failed]\n    D --> F([Order Complete])\n    E --> G([Order Cancelled])",
  "preview_url": "http://localhost:8000/v1/diagrams/diag_550e8400-flow-001/preview",
  "export_urls": {
    "svg": "http://localhost:8000/v1/diagrams/diag_550e8400-flow-001/export?format=svg",
    "png": "http://localhost:8000/v1/diagrams/diag_550e8400-flow-001/export?format=png",
    "pdf": "http://localhost:8000/v1/diagrams/diag_550e8400-flow-001/export?format=pdf",
    "mermaid": "http://localhost:8000/v1/diagrams/diag_550e8400-flow-001/export?format=mermaid"
  },
  "metadata": {
    "steps_count": 7,
    "decision_points": 1,
    "paths_count": 2,
    "generated_at": "2025-09-20T14:30:00Z",
    "processing_time_ms": 1600,
    "llm_used": "openai-gpt-4"
  }
}
```

### Common Diagram Operations

#### GET /diagrams/{diagram_id}

Retrieve a generated diagram.

**Response (200 OK):**

```json
{
  "diagram_id": "diag_550e8400-seq-001",
  "type": "sequence",
  "title": "User Authentication Flow",
  "mermaid_code": "sequenceDiagram...",
  "preview_url": "http://localhost:8000/v1/diagrams/diag_550e8400-seq-001/preview",
  "metadata": {
    "created_at": "2025-09-20T14:30:00Z",
    "updated_at": "2025-09-20T14:30:00Z",
    "status": "generated"
  }
}
```

#### PUT /diagrams/{diagram_id}

Update an existing diagram.

**Request Body:**

```json
{
  "title": "Updated User Authentication Flow",
  "mermaid_code": "sequenceDiagram...",
  "change_summary": "Added error handling and timeout scenarios"
}
```

#### DELETE /diagrams/{diagram_id}

Delete a diagram.

**Response (204 No Content)**

#### GET /diagrams/{diagram_id}/export

Export diagram in specified format.

**Query Parameters:**

- `format` (string, required): Export format (`svg`, `png`, `pdf`, `mermaid`)
- `quality` (string, optional): Image quality for raster formats (`low`, `medium`, `high`)
- `theme` (string, optional): Diagram theme (`default`, `dark`, `forest`, `neutral`)

#### GET /diagrams

List user's diagrams.

**Query Parameters:**

- `type` (string, optional): Filter by diagram type (`sequence`, `architecture`, `usecase`, `flowchart`)
- `limit` (integer, optional): Maximum diagrams to return (default: 20)
- `offset` (integer, optional): Pagination offset (default: 0)
- `search` (string, optional): Search in diagram titles

**Response (200 OK):**

```json
{
  "diagrams": [
    {
      "diagram_id": "diag_550e8400-seq-001",
      "type": "sequence",
      "title": "User Authentication Flow",
      "created_at": "2025-09-20T14:30:00Z",
      "updated_at": "2025-09-20T14:30:00Z",
      "preview_url": "http://localhost:8000/v1/diagrams/diag_550e8400-seq-001/preview"
    }
  ],
  "pagination": {
    "total": 12,
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
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
  "preferences": {
    "preferred_llm": "openai",
    "default_srs_template": "standard",
    "default_diagram_theme": "default",
    "auto_generate_diagrams": true
  },
  "usage_stats": {
    "srs_generated": 15,
    "wireframes_created": 8,
    "diagrams_generated": 23,
    "conversations_started": 12
  },
  "created_at": "2025-09-01T10:00:00Z",
  "updated_at": "2025-09-20T14:30:00Z"
}
```

### PUT /users/me

Update user profile.

**Request Body:**

```json
{
  "full_name": "John Smith",
  "organization": "Updated Corp",
  "preferences": {
    "preferred_llm": "claude",
    "default_srs_template": "agile",
    "auto_generate_diagrams": false
  }
}
```

## Health Check

### GET /health

Get service health status.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "timestamp": "2025-09-20T14:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "llm_providers": {
      "openai": "healthy",
      "claude": "healthy"
    },
    "file_storage": "healthy",
    "diagram_renderer": "healthy"
  },
  "uptime_seconds": 86400
}
```

## Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "code": "DIAGRAM_GENERATION_ERROR",
    "message": "Unable to generate diagram from provided description",
    "details": {
      "field": "mermaid_syntax",
      "issue": "Invalid sequence diagram syntax"
    },
    "timestamp": "2025-09-20T14:30:00Z",
    "request_id": "req_550e8400-e29b-41d4-a716-446655440000"
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
- **422 Unprocessable Entity**: Request valid but cannot be processed
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Service temporarily unavailable

## Rate Limiting

API requests are rate limited per user:

- **Authentication**: 10 requests per minute
- **SRS Generation**: 5 requests per minute
- **Wireframe Generation**: 3 requests per minute
- **Diagram Generation**: 10 requests per minute
- **AI Conversations**: 60 requests per minute
- **General API**: 100 requests per minute

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1695220800
```

## WebSocket Connection

For real-time AI conversations and diagram generation progress:

**Connection URL**: `ws://localhost:8000/v1/conversations/{conversation_id}/ws`

**Message Format:**

```json
{
  "type": "message",
  "content": "Generate a sequence diagram for user login process",
  "timestamp": "2025-09-20T14:30:00Z"
}
```

**Response Format:**

```json
{
  "type": "diagram_progress",
  "content": "Generating sequence diagram...",
  "progress": 75,
  "diagram_id": "diag_550e8400-seq-001",
  "timestamp": "2025-09-20T14:30:15Z"
}
```

## Development Setup

### Running the AI API Locally

1. **Start the development server:**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access API documentation:**

   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Test diagram generation:**
   ```bash
   curl -X POST "http://localhost:8000/v1/diagrams/sequence/generate" \
        -H "Authorization: Bearer <token>" \
        -H "Content-Type: application/json" \
        -d '{"title": "Test Sequence", "description": "Simple test sequence diagram"}'
   ```

### Environment Variables

Required environment variables for local development:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/bacopilot
SECRET_KEY=your-secret-key-here
GOOGLE_AI_API_KEY=your-google-ai-api-key
CLAUDE_API_KEY=your-claude-api-key  # Optional
DIAGRAM_RENDERER_URL=http://localhost:8080  # Mermaid renderer service
LOG_LEVEL=DEBUG
```

### Technology Stack

| Component             | Technology           | Purpose                           |
| --------------------- | -------------------- | --------------------------------- |
| **Web Framework**     | FastAPI              | API development and documentation |
| **AI Integration**    | LangChain, LangGraph | LLM orchestration and chaining    |
| **Database**          | PostgreSQL 14+       | Primary data storage              |
| **Diagram Rendering** | Mermaid CLI          | Diagram generation and export     |
| **Authentication**    | JWT + bcrypt         | User security                     |
| **Documentation**     | OpenAPI/Swagger      | API documentation                 |
| **Containerization**  | Docker               | Deployment packaging              |

This AI API specification covers all endpoints provided by the BA Copilot AI Services backend. The service is designed as a modular monolith that focuses specifically on AI-powered document and diagram generation capabilities.
