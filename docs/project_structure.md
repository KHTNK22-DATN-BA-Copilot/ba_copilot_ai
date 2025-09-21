# Project Structure

This document outlines the simplified project structure for the BA Copilot AI Core Services backend, following a modular monolith approach.

## Directory Structure

```
ba_copilot_ai/
├── app/                                # Main application package
│   ├── __init__.py
│   ├── main.py                         # FastAPI application entry point
│   ├── config.py                       # Configuration management
│   │
│   ├── core/                           # Core application components
│   │   ├── __init__.py
│   │   ├── auth.py                     # Authentication utilities
│   │   ├── security.py                 # Security utilities (JWT, hashing)
│   │   ├── database.py                 # Database connection and setup
│   │   └── exceptions.py               # Custom exceptions
│   │
│   ├── api/                            # API routes and dependencies
│   │   ├── __init__.py
│   │   ├── dependencies.py             # FastAPI dependencies
│   │   ├── middleware.py               # Custom middleware
│   │   └── v1/                         # API version 1
│   │       ├── __init__.py
│   │       ├── router.py               # Main router
│   │       ├── auth.py                 # Authentication endpoints
│   │       ├── users.py                # User management endpoints
│   │       ├── srs.py                  # SRS generation endpoints
│   │       ├── wireframes.py           # Wireframe generation endpoints
│   │       ├── conversations.py        # AI conversation endpoints
│   │       └── health.py               # Health check endpoints
│   │
│   ├── models/                         # Database models
│   │   ├── __init__.py
│   │   ├── base.py                     # Base model class
│   │   ├── user.py                     # User model
│   │   ├── document.py                 # Document/SRS model
│   │   ├── wireframe.py                # Wireframe model
│   │   └── conversation.py             # Conversation model
│   │
│   ├── schemas/                        # Pydantic schemas for API
│   │   ├── __init__.py
│   │   ├── user.py                     # User schemas
│   │   ├── auth.py                     # Authentication schemas
│   │   ├── srs.py                      # SRS schemas
│   │   ├── wireframe.py                # Wireframe schemas
│   │   └── conversation.py             # Conversation schemas
│   │
│   ├── services/                       # Business logic modules
│   │   ├── __init__.py
│   │   ├── user_service.py             # User management logic
│   │   ├── auth_service.py             # Authentication logic
│   │   ├── srs_service.py              # SRS generation logic
│   │   ├── wireframe_service.py        # Wireframe generation logic
│   │   ├── conversation_service.py     # AI conversation logic
│   │   └── llm_service.py              # LLM integration logic
│   │
│   ├── repositories/                   # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py                     # Base repository
│   │   ├── user.py                     # User repository
│   │   ├── document.py                 # Document repository
│   │   ├── wireframe.py                # Wireframe repository
│   │   └── conversation.py             # Conversation repository
│   │
│   └── utils/                          # Utility functions
│       ├── __init__.py
│       ├── validators.py               # Input validators
│       ├── formatters.py               # Data formatters
│       ├── file_handler.py             # File upload/download handling
│       └── websocket.py                # WebSocket utilities
│
├── tests/                              # Test suites
│   ├── __init__.py
│   ├── conftest.py                     # Pytest configuration
│   ├── test_auth.py                    # Authentication tests
│   ├── test_users.py                   # User management tests
│   ├── test_srs.py                     # SRS generation tests
│   ├── test_wireframes.py              # Wireframe generation tests
│   ├── test_conversations.py           # Conversation tests
│   └── fixtures/                       # Test fixtures
│       ├── __init__.py
│       ├── users.py                    # User fixtures
│       └── documents.py                # Document fixtures
│
├── alembic/                            # Database migrations
│   ├── versions/                       # Migration files
│   ├── env.py                          # Alembic environment
│   ├── script.py.mako                  # Migration template
│   └── alembic.ini                     # Alembic configuration
│
├── docs/                               # Documentation
│   ├── api/                            # API documentation
│   │   └── openapi.json                # OpenAPI specification
│   ├── architecture/                   # Architecture docs
│   │   ├── system_design.md
│   │   └── database_schema.md
│   └── guides/                         # User guides
│       ├── development.md
│       └── deployment.md
│
├── scripts/                            # Utility scripts
│   ├── run_migrations.py               # Database migration runner
│   ├── create_admin.py                 # Admin user creator
│   └── dev_setup.py                    # Development setup
│
├── .env.template                       # Environment variables template
├── .gitignore                          # Git ignore rules
├── .dockerignore                       # Docker ignore rules
├── Dockerfile                          # Docker configuration
├── docker-compose.yml                  # Local development setup
├── pyproject.toml                      # Python project configuration
├── Makefile                            # Development commands
├── README.md                           # Project documentation
└── requirements.txt                    # Python dependencies (alternative to pyproject.toml)
```

## Key Design Principles

### 1. **Modular Monolith Architecture**

The application is organized as a single deployable unit with clear module boundaries that can later be extracted into separate services if needed.

### 2. **Clean Architecture Layers**

- **API Layer** (`api/`): Handles HTTP requests, validation, and routing
- **Service Layer** (`services/`): Contains business logic and orchestration
- **Repository Layer** (`repositories/`): Manages data access and database operations
- **Model Layer** (`models/`): Defines database entities and relationships
- **Schema Layer** (`schemas/`): Defines API input/output contracts

### 3. **Single Responsibility**

Each module has a focused responsibility:

- Services handle business logic
- Repositories handle data access
- Schemas handle API contracts
- Models define data structures

### 4. **Dependency Management**

Clear dependency flow from API → Services → Repositories → Models, avoiding circular dependencies.

### 5. **Testability**

Simplified test structure focusing on:

- Unit tests for individual components
- Integration tests for API endpoints
- Fixtures for test data management

## Module Organization

### **Core Application** (`app/core/`)

Provides foundational components used across all modules:

- Database configuration and connection management
- Authentication and security utilities
- Custom exceptions and error handling
- Application configuration

### **API Layer** (`app/api/`)

Handles all HTTP interactions:

- Route definitions and endpoint logic
- Request/response validation using Pydantic schemas
- Authentication middleware and dependencies
- CORS and other middleware configuration

### **Business Logic** (`app/services/`)

Contains all business rules and orchestration:

- User management and authentication logic
- SRS document generation and processing
- Wireframe creation and management
- AI conversation handling and LLM integration

### **Data Access** (`app/repositories/`)

Manages all database operations:

- CRUD operations for each entity
- Complex queries and data aggregation
- Database transaction management
- Query optimization

### **Data Models** (`app/models/`)

Defines database schema and relationships:

- SQLAlchemy ORM models
- Database relationships and constraints
- Model-level validation and business rules

## Development Benefits

### **Rapid Development**

- Single codebase with direct function calls
- Shared database transactions
- Simple debugging and testing
- Fast development iteration cycles

### **Clear Boundaries**

- Well-defined module interfaces
- Easy to understand data flow
- Straightforward dependency management
- Simple deployment and configuration

### **Migration Ready**

- Service boundaries are clearly defined
- Repositories provide data access abstraction
- Services can be extracted with minimal refactoring
- Database can be split along service lines

## Deployment Strategy

### **Phase 1: Monolith Deployment (Current)**

**Local Development:**

```bash
# Start with Docker Compose
docker-compose up -d

# Or run locally with virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Production Deployment:**

```bash
# Single container deployment
docker build -t ba-copilot-ai .
docker run -p 8000:8000 ba-copilot-ai

# Or with Docker Compose for production
docker-compose -f docker-compose.prod.yml up -d
```

### **Phase 2: Microservices Migration (Future)**

**Horizontal Scaling (Interim):**

```bash
# Scale the monolith horizontally
docker-compose up --scale app=3
```

**Service Extraction (Advanced):**

```bash
# Extract AI conversation service as separate deployment
# 1. Create separate repository for conversation service
# 2. Convert internal function calls to HTTP/gRPC calls
# 3. Split database by service boundaries
# 4. Deploy services independently
```

### **Scaling Considerations**

- **Database Scaling**: Use PostgreSQL read replicas for read-heavy workloads
- **Load Balancing**: Add NGINX or cloud load balancer for multiple instances
- **Service Extraction Priority**: Move high-traffic or resource-intensive modules first
- **Data Migration**: Plan database splitting strategy before service extraction

This structure provides immediate development velocity while maintaining clear paths for future architectural evolution.
