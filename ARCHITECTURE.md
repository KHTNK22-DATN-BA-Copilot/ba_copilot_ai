# BA Copilot AI Service - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  (Frontend, Mobile App, CLI, Postman, curl, etc.)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FASTAPI APPLICATION                          │
│                         (main.py)                                │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   GET /      │  │ GET /health  │  │POST /ai/gen  │         │
│  │   Root       │  │ Health Check │  │   Generate   │         │
│  └──────────────┘  └──────────────┘  └──────┬───────┘         │
│                                              │                  │
│  ┌───────────────────────────────────────────┘                 │
│  │  CORS Middleware                                             │
│  │  Error Handling                                              │
│  │  Request Validation (Pydantic)                               │
│  └──────────────────────────────────────────────────────────┐  │
└────────────────────────────────┬────────────────────────────┘  │
                                 │                                │
                                 ▼                                │
┌─────────────────────────────────────────────────────────────────┐
│                   LANGGRAPH WORKFLOW                             │
│                    (ai_workflow.py)                              │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Intent Classification Node                  │   │
│  │             (Gemini 1.5 Pro - Temp: 0.1)                │   │
│  │  Analyze: "srs", "wireframe", or "diagram"             │   │
│  └───────────────────────┬─────────────────────────────────┘   │
│                          │                                      │
│            ┌─────────────┼─────────────┐                       │
│            │             │             │                       │
│            ▼             ▼             ▼                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │
│  │  SRS Node   │ │ Wireframe   │ │  Diagram    │             │
│  │             │ │    Node     │ │    Node     │             │
│  │  ┌───────┐  │ │             │ │  ┌───────┐  │             │
│  │  │Gemini │  │ │ ┌────────┐  │ │  │Gemini │  │             │
│  │  │1.5 Pro│  │ │ │ Figma  │  │ │  │+ Figma│  │             │
│  │  │       │  │ │ │  MCP   │  │ │  │  MCP  │  │             │
│  │  └───┬───┘  │ │ └────┬───┘  │ │  └───┬───┘  │             │
│  │      │      │ │      │      │ │      │      │             │
│  │  Generate   │ │  Generate   │ │  Generate   │             │
│  │   SRS Doc   │ │  Wireframe  │ │   Diagram   │             │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘             │
│         │               │               │                     │
│         └───────────────┼───────────────┘                     │
│                         │                                      │
│                         ▼                                      │
│         ┌─────────────────────────────┐                       │
│         │   Pydantic Validation       │                       │
│         │   (models/srs.py)           │                       │
│         │   (models/wireframe.py)     │                       │
│         │   (models/diagram.py)       │                       │
│         └─────────────┬───────────────┘                       │
└───────────────────────┼─────────────────────────────────────  │
                        │                                        │
                        ▼                                        │
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE LAYER                                │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │     SRS      │   │  Wireframe   │   │   Diagram    │       │
│  │   Response   │   │   Response   │   │   Response   │       │
│  │              │   │              │   │              │       │
│  │  type: "srs" │   │ type: "wire" │   │ type: "diag" │       │
│  │  response: { │   │ response: {  │   │ response: {  │       │
│  │   title      │   │  figma_link  │   │  figma_link  │       │
│  │   func_req   │   │  editable    │   │  editable    │       │
│  │   non_func   │   │  description │   │  description │       │
│  │   detail(MD) │   │ }            │   │ }            │       │
│  │ }            │   │              │   │              │       │
│  └──────────────┘   └──────────────┘   └──────────────┘       │
└─────────────────────────────────────────────────────────────────┘

                              ▲
                              │
                              │
                   ┌──────────┴──────────┐
                   │   External APIs     │
                   ├─────────────────────┤
                   │ • Google Gemini API │
                   │ • Figma API (mock)  │
                   └─────────────────────┘
```

## Component Details

### 1. FastAPI Layer (main.py)
**Responsibilities:**
- HTTP request handling
- CORS configuration
- Input validation (Pydantic)
- Error handling
- API documentation (Swagger/ReDoc)
- Health checks

**Endpoints:**
- `GET /` - Service info
- `GET /health` - Health check
- `POST /ai/generate` - Main generation endpoint

### 2. LangGraph Workflow (ai_workflow.py)
**Responsibilities:**
- Orchestrate AI workflow
- Intent classification
- Route to appropriate generator
- State management

**Nodes:**
1. **Intent Classifier**
   - Uses Gemini 1.5 Pro
   - Temperature: 0.1 (consistent classification)
   - Output: "srs", "wireframe", or "diagram"

2. **SRS Node**
   - Generates Software Requirements Specification
   - Uses Gemini 1.5 Pro (temp: 0.3)
   - Structured JSON output
   - Markdown detailed section

3. **Wireframe Node**
   - Generates Figma wireframe link
   - Uses Figma MCP (currently mock)
   - Returns editable Figma URL

4. **Diagram Node**
   - Generates diagram description via Gemini
   - Creates Figma diagram via MCP
   - Returns editable Figma URL

### 3. Pydantic Models (models/)
**Responsibilities:**
- Response schema validation
- Type safety
- Automatic documentation

**Models:**
- `SRSResponse` / `SRSOutput`
- `WireframeResponse` / `WireframeOutput`
- `DiagramResponse` / `DiagramOutput`

### 4. Figma Integration (figma_mcp.py)
**Current:** Mock implementation with UUID-based links
**Future:** Real Figma API integration

## Data Flow

### Example: SRS Generation

```
1. Client Request
   POST /ai/generate
   {
     "message": "Tạo SRS cho hệ thống quản lý thư viện"
   }
   ↓

2. FastAPI Validation
   - Validate request body
   - Check API key configured
   ↓

3. LangGraph Invocation
   ai_graph.invoke({"user_message": "Tạo SRS cho..."})
   ↓

4. Intent Classification
   Gemini analyzes → "srs"
   ↓

5. Route to SRS Node
   ↓

6. SRS Generation
   Gemini generates structured SRS
   ↓

7. Pydantic Validation
   Validate response against SRSResponse schema
   ↓

8. Return Response
   {
     "type": "srs",
     "response": {
       "title": "Hệ thống quản lý thư viện",
       "functional_requirements": "...",
       "non_functional_requirements": "...",
       "detail": "# SRS Document\n\n..."
     }
   }
```

## Deployment Architecture

```
┌──────────────────────────────────────────────────────┐
│                 Docker Host                          │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │         Docker Network: ba-network          │    │
│  │                                             │    │
│  │  ┌──────────────────┐  ┌──────────────┐   │    │
│  │  │   ai-service     │  │      db      │   │    │
│  │  │  (FastAPI App)   │  │ (PostgreSQL) │   │    │
│  │  │                  │  │              │   │    │
│  │  │  Port: 8000      │  │  Port: 5432  │   │    │
│  │  │                  │  │              │   │    │
│  │  │  Env: .env       │  │  Volume:     │   │    │
│  │  │  Volume: ./:/app │  │  postgres_   │   │    │
│  │  │                  │  │  data        │   │    │
│  │  └────────┬─────────┘  └──────────────┘   │    │
│  │           │                                │    │
│  └───────────┼────────────────────────────────┘    │
│              │                                      │
└──────────────┼──────────────────────────────────────┘
               │
               │ Port Mapping: 8000:8000
               ▼
       ┌───────────────┐
       │    Clients    │
       │ (localhost:   │
       │    8000)      │
       └───────────────┘
```

## Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### AI/ML
- **LangChain**: LLM framework
- **LangGraph**: Workflow orchestration
- **Google Gemini 1.5 Pro**: LLM model

### Database
- **PostgreSQL 15**: Relational database
- **SQLAlchemy**: ORM

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

### Security
- **python-dotenv**: Environment variable management
- **CORS middleware**: Cross-origin resource sharing

## Scalability Considerations

### Current Setup
- Single container deployment
- Direct LLM API calls
- Synchronous processing

### Future Improvements
1. **Horizontal Scaling**
   - Multiple ai-service instances
   - Load balancer (nginx)

2. **Caching**
   - Redis for response caching
   - Reduce LLM API calls

3. **Async Processing**
   - Celery task queue
   - Background job processing

4. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Log aggregation (ELK stack)

5. **API Gateway**
   - Rate limiting
   - Authentication
   - Request throttling

## Security Architecture

### Current Implementation
- Environment variable protection (.env ignored)
- API key security
- CORS configuration

### Production Recommendations
1. **Authentication**
   - JWT tokens
   - API keys per client
   - OAuth2 integration

2. **Authorization**
   - Role-based access control
   - Request quotas

3. **Network Security**
   - HTTPS/TLS
   - Reverse proxy (nginx)
   - Firewall rules

4. **Input Validation**
   - Pydantic schemas
   - SQL injection prevention
   - XSS protection

## Performance Metrics

### Expected Response Times
- **Intent Classification**: ~1-2s
- **SRS Generation**: ~5-10s
- **Wireframe Generation**: <1s (mock)
- **Diagram Generation**: ~3-7s

### Resource Usage
- **Memory**: ~500MB-1GB per container
- **CPU**: Variable based on LLM calls
- **Network**: Depends on LLM API latency

## Error Handling

### Error Types
1. **Client Errors (4xx)**
   - Invalid request format
   - Missing required fields

2. **Server Errors (5xx)**
   - LLM API failures
   - Internal processing errors
   - Database connection issues

3. **External API Errors**
   - Google API rate limits
   - API key issues
   - Network timeouts

### Recovery Strategies
- Automatic retry with exponential backoff
- Fallback responses
- Error logging and monitoring
- Circuit breaker pattern (future)
