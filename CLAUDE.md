# BA Copilot AI Services - LLM Agent Guide

**Repository**: AI Services Backend (1 of 3 in BA Copilot ecosystem)  
**Technology Stack**: FastAPI + Python 3.11+ + PostgreSQL + Redis + Docker  
**Architecture**: Modular Monolith (Migration-ready to Microservices)  
**Current Phase**: MVP Development (Target: November 1st, 2025)

## Project Overview

BA Copilot AI Services provides AI-powered document generation, wireframe creation, diagram generation, and intelligent conversation management for Business Analysts. This is the specialized AI backend that integrates with LLMs (OpenAI GPT-4, Claude-3) to automate business analysis artifacts.

### Core Services

- **SRS Generator**: Software Requirements Specification document generation
- **Wireframe Generator**: UI prototype creation from text descriptions
- **Diagram Generator**: Architecture, sequence, use case, and flowchart diagrams
- **AI Conversation**: Context-aware chat with conversation history
- **Health Monitoring**: System health and performance monitoring

### Repository Context

This is 1 of 3 repositories:

1. **Frontend Repository**: NextJS + ReactJS + TailwindCSS user interface
2. **Backend Repository**: Core business logic and database operations
3. **AI Services Repository** (This repo): AI-powered generation services

## Project Structure

```
ba_copilot_ai/
├── src/                           # Main application source
│   ├── main.py                    # FastAPI application entry point
│   ├── core/                      # Core components (config, auth, db)
│   ├── api/v1/                    # API routes and endpoints
│   │   ├── router.py              # Main API router
│   │   └── endpoints/             # Service endpoints
│   │       ├── srs.py             # SRS generation endpoints
│   │       ├── wireframes.py      # Wireframe generation endpoints
│   │       ├── conversations.py   # AI conversation endpoints
│   │       ├── diagrams.py        # Diagram generation endpoints
│   │       └── health.py          # Health check endpoints
│   ├── services/                  # Business logic modules
│   ├── shared/                    # Shared utilities and models
│   └── alembic/                   # Database migrations
├── tests/                         # Test suites (pytest)
├── docs/                          # Documentation
├── infrastructure/                # Docker and deployment configs
├── scripts/                       # Utility scripts
├── Makefile                       # Development automation
├── pyproject.toml                 # Python project configuration
└── docker-compose.yml             # Local development environment
```

## Development Environment

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 14+ (or use Docker)
- Redis 6.2+ (or use Docker)

### Environment Setup

```bash
# Activate virtual environment (Windows)
.venv/Scripts/activate

# Activate virtual environment (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup development environment
make setup

# Start services with Docker
make docker-up

# Run database migrations
make migrate
```

### Environment Variables

```bash
# Copy template and configure
cp .env.template .env

# Required variables:
DATABASE_URL=postgresql://username:password@localhost:5432/bacopilot
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key
JWT_SECRET_KEY=your_jwt_secret
```

## Development Commands

### Core Development

```bash
# Start development server
make dev                    # uvicorn with auto-reload
python src/main.py         # Direct Python execution

# Database operations
make migrate               # Run migrations
make migration msg="description"  # Create new migration
make db-reset              # Reset database (development only)

# Docker operations
make docker-up             # Start all services
make docker-down           # Stop all services
make docker-build          # Rebuild containers
```

### Testing & Quality

```bash
# Run tests
make test                  # All tests
make test-unit             # Unit tests only
make test-integration      # Integration tests only
make test-coverage         # Tests with coverage report

# Code quality
make lint                  # Run linting (flake8, black)
make format                # Format code (black, isort)
make type-check            # Type checking (mypy)
```

## Coding Standards

### Python Standards

- **Python Version**: 3.11+
- **Code Style**: Black formatting, PEP 8 compliance
- **Import Organization**: isort with profile "black"
- **Type Hints**: Required for all functions and class methods
- **Docstrings**: Google-style docstrings for all public functions/classes

### Code Organization

```python
# File structure pattern
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.auth import get_current_user
from schemas.srs import SRSRequest, SRSResponse
from services.srs_service import SRSService
from models.user import User

# Constants at module level
ROUTER_PREFIX = "/srs"
ROUTER_TAGS = ["srs"]

# Router definition
router = APIRouter(prefix=ROUTER_PREFIX, tags=ROUTER_TAGS)
```

### Naming Conventions

- **Files/Modules**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Database Tables**: `snake_case`
- **API Endpoints**: `kebab-case` in URLs
- **Environment Variables**: `UPPER_SNAKE_CASE`

### Error Handling

```python
# Standard error handling pattern
from fastapi import HTTPException, status
from core.exceptions import ServiceException

async def endpoint_function():
    try:
        result = await service_operation()
        return result
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

## Database Standards

### Model Definitions

```python
# SQLAlchemy model pattern
from sqlalchemy import Column, String, Text, DateTime, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from shared.database.base import Base

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="documents")
```

### Migration Standards

```python
# Alembic migration pattern
def upgrade() -> None:
    """Create documents table."""
    op.create_table(
        'documents',
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text()),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('document_id')
    )
    op.create_index('idx_documents_user_id', 'documents', ['user_id'])
    op.create_index('idx_documents_created_at', 'documents', ['created_at'])

def downgrade() -> None:
    """Drop documents table."""
    op.drop_table('documents')
```

## Testing Standards

### Test Structure

```python
# Test file pattern: test_<module_name>.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from core.database import get_db
from tests.conftest import TestingSessionLocal, override_get_db

# Test class organization
class TestSRSEndpoints:
    """Test suite for SRS generation endpoints."""

    def test_generate_srs_success(self, client: TestClient, db: Session):
        """Test successful SRS generation."""
        # Arrange
        payload = {
            "project_name": "Test Project",
            "requirements": "Create a user management system"
        }

        # Act
        response = client.post("/v1/srs/generate", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["project_name"] == payload["project_name"]
        assert "document_id" in data

    def test_generate_srs_invalid_input(self, client: TestClient):
        """Test SRS generation with invalid input."""
        payload = {"project_name": ""}  # Invalid empty name

        response = client.post("/v1/srs/generate", json=payload)

        assert response.status_code == 422
```

### Test Categories

- **Unit Tests**: `tests/test_<service_name>.py` - Business logic testing
- **Integration Tests**: API endpoint testing with database
- **Fixtures**: Shared test data in `tests/conftest.py`

### Test Commands

```bash
# Run specific test categories
pytest tests/test_srs.py -v                    # Single service tests
pytest tests/ -k "test_generate" -v            # Pattern matching
pytest tests/ --cov=src --cov-report=html      # Coverage report
pytest tests/ -x                               # Stop on first failure
```

## API Standards

### Endpoint Patterns

```python
# RESTful endpoint patterns
POST   /v1/srs/generate           # Create new SRS document
GET    /v1/srs/{document_id}      # Get specific document
GET    /v1/srs                    # List user documents
PUT    /v1/srs/{document_id}      # Update document
DELETE /v1/srs/{document_id}      # Delete document

# Service-specific patterns
POST   /v1/wireframes/generate    # Generate wireframe
GET    /v1/wireframes/{wireframe_id}
POST   /v1/conversations/send     # Send message
GET    /v1/conversations/{conversation_id}/messages
POST   /v1/diagrams/generate      # Generate diagram
```

### Request/Response Schemas

```python
# Pydantic schema pattern
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class SRSRequest(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=255)
    requirements: str = Field(..., min_length=10)
    template_type: Optional[str] = Field(default="standard")

class SRSResponse(BaseModel):
    document_id: UUID
    project_name: str
    content: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
```

## Logging Standards

### Logging Configuration

```python
import logging
import sys
from core.config import settings

# Logging setup pattern
def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/app.log") if settings.LOG_FILE else None
        ]
    )

# Usage in modules
logger = logging.getLogger(__name__)

# Logging patterns
logger.info(f"Processing SRS generation for user {user_id}")
logger.warning(f"Rate limit exceeded for user {user_id}")
logger.error(f"LLM service error: {str(error)}", exc_info=True)
logger.debug(f"Request payload: {payload}")
```

### Log Levels

- **DEBUG**: Detailed debugging information (development only)
- **INFO**: General application flow and business events
- **WARNING**: Recoverable errors and important notices
- **ERROR**: Error conditions that don't stop the application
- **CRITICAL**: Serious errors that may stop the application

## Security Standards

### Authentication & Authorization

```python
# JWT authentication pattern
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from core.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Extract and validate JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return await get_user_by_id(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

### Input Validation

- Use Pydantic models for all API inputs
- Validate file uploads and sizes
- Sanitize all text inputs before LLM processing
- Implement rate limiting per user/endpoint

## AI/LLM Integration Standards

### LLM Service Pattern

```python
# LLM client pattern
from typing import Dict, Any, Optional
import openai
import anthropic
from core.config import settings

class LLMService:
    """Centralized LLM integration service."""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_content(
        self,
        prompt: str,
        provider: str = "openai",
        model: str = "gpt-4",
        **kwargs
    ) -> str:
        """Generate content using specified LLM provider."""
        try:
            if provider == "openai":
                response = await self._call_openai(prompt, model, **kwargs)
            elif provider == "anthropic":
                response = await self._call_anthropic(prompt, model, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            return response
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise

    async def _call_openai(self, prompt: str, model: str, **kwargs) -> str:
        """Call OpenAI API."""
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.choices[0].message.content
```

### Prompt Engineering Standards

- Store prompts in configuration files or constants
- Use template patterns for dynamic content injection
- Include clear instructions and output format specifications
- Test prompts with various input scenarios
- Implement fallback prompts for error cases

## Docker & Deployment

### Docker Commands

```bash
# Development environment
docker-compose up -d                    # Start all services
docker-compose down                     # Stop all services
docker-compose logs -f api              # View API logs
docker-compose exec api bash            # Access API container
docker-compose exec postgres psql -U bacopilot -d bacopilot  # Database access

# Production commands
docker-compose -f docker-compose.prod.yml up -d    # Production deployment
docker-compose exec api alembic upgrade head       # Run migrations
```

### Service Health Checks

```bash
# Health check endpoints
curl http://localhost:8000/v1/health           # Basic health
curl http://localhost:8000/v1/health/detailed  # Detailed health with dependencies
```

## Performance & Monitoring

### Performance Guidelines

- Use async/await for I/O operations
- Implement connection pooling for database
- Cache frequently accessed data with Redis
- Monitor LLM API usage and costs
- Implement request timeouts and retries

### Monitoring Endpoints

```python
# Health check patterns
@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with dependencies."""
    try:
        # Check database
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "services": {
            "database": db_status,
            "redis": "healthy",  # Add actual check
            "llm_providers": "healthy"  # Add actual check
        },
        "timestamp": datetime.utcnow()
    }
```

## Documentation References

### Project Documentation

- **Architecture**: `docs/system_architecture.md`
- **Database Schema**: `docs/database_documentation.md`
- **API Specifications**: `docs/ai_api_specs.md`
- **Project Plan**: `docs/project_plan.md`
- **Service Flows**:
  - `docs/srs_generator_flow.md`
  - `docs/wireframe_generator_flow.md`
  - `docs/ai_conversation_flow.md`
  - `docs/architecture_diagram_flow.md`

### Key Configuration Files

- **Main Config**: `src/core/config.py`
- **Database Models**: `src/shared/database/models/`
- **API Schemas**: `src/api/v1/schemas/`
- **Migration Config**: `src/alembic.ini`
- **Dependencies**: `pyproject.toml`

### External Documentation

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Pydantic**: https://docs.pydantic.dev/
- **Alembic**: https://alembic.sqlalchemy.org/
- **OpenAI API**: https://platform.openai.com/docs
- **Anthropic API**: https://docs.anthropic.com/

## Debugging Guide

### Common Issues & Solutions

1. **Database Connection Issues**

   ```bash
   # Check database status
   docker-compose ps postgres
   docker-compose logs postgres

   # Test connection
   docker-compose exec postgres psql -U bacopilot -d bacopilot -c "SELECT version();"
   ```

2. **Migration Issues**

   ```bash
   # Check migration status
   alembic current
   alembic history

   # Manual migration
   alembic upgrade head
   alembic downgrade -1
   ```

3. **LLM API Issues**

   ```bash
   # Check API keys in environment
   echo $OPENAI_API_KEY
   echo $ANTHROPIC_API_KEY

   # Test API connectivity
   curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
   ```

4. **Import/Path Issues**

   ```bash
   # Check Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

   # Verify imports
   python -c "from src.core.config import settings; print('✅ Import successful')"
   ```

### Development Workflow

1. **Feature Development**

   ```bash
   # Create feature branch
   git checkout -b feature/feature-name

   # Setup environment
   make setup
   make docker-up

   # Develop with tests
   make test-watch  # Continuous testing
   make dev         # Development server

   # Code quality checks
   make lint
   make type-check
   ```

2. **Before Commit**

   ```bash
   # Run full test suite
   make test-coverage

   # Format and lint
   make format
   make lint

   # Check migrations
   make migration-check
   ```

This guide provides comprehensive information for LLM agents working on the BA Copilot AI Services codebase. Follow these patterns and standards to maintain code quality and consistency.
