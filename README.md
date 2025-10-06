# BA Copilot AI - AI Services Backend

**AI Services Repository** for **Business Analyst Copilot Artificial Intelligence** _(BA Copilot)_, providing comprehensive AI-powered services and APIs for automated document generation, diagram creation, and intelligent conversations.

> **📋 Repository Context**: This is the **AI Services Backend** - one of three repositories in the BA Copilot ecosystem:
>
> 1. **Frontend Repository**: NextJS + ReactJS + TailwindCSS user interface
> 2. **Backend Repository**: Core business logic and database operations
> 3. **AI Services Repository** (This repo): AI-powered generation services

## 🎯 Overview

BA Copilot AI Services is a specialized backend platform that leverages advanced Large Language Models (LLMs) to automate the creation of business analysis artifacts. The platform provides intelligent tools for generating Software Requirements Specifications (SRS), creating wireframe prototypes, generating various diagrams, and managing AI-powered conversations.

## 📋 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#️-technology-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [Documentation](#-documentation)
- [License](#license)

## ✨ Key Features

### 🔥 Core AI Services

- **SRS Generator**: Automated creation of Software Requirements Specification documents from natural language input and uploaded documents
- **Diagram Generator**: AI-powered creation of sequence, architecture, use case, and flowchart diagrams from descriptions or requirements
- **Wireframe Generator**: AI-powered conversion of textual requirements into interactive wireframe prototypes
- **AI Conversation Manager**: Intelligent chat system with context management, multi-LLM routing, and conversation history
- **Document Processing**: Advanced parsing and analysis of business documents in various formats
  ```powershell
  # For Docker development (Windows PowerShell)
  Set-Location 'D:\Do_an_tot_nghiep\ba_copilot_ai'
  Copy-Item 'infrastructure\.env' '.env' -Force  # ensure .env at project root
  docker-compose -f infrastructure/docker-compose.yml up --build -d
  ```
- **RESTful API Design**: Industry-standard REST APIs with comprehensive OpenAPI documentation
- **Microservices Architecture**: Independently scalable services with clear domain boundaries

  ```powershell
  # Activate virtual environment first
  .venv\Scripts\Activate

  # Start the server
  Set-Location 'D:\Do_an_tot_nghiep\ba_copilot_ai\src'
  python main.py
  ```

### Architecture Approach

- **Phase 1 (Current)**: Monolithic deployment with modular service boundaries
- **Phase 2 (Future)**: Gradual extraction to independent microservices

The system starts as a single FastAPI application with well-defined internal service modules that can be extracted into separate services when needed. This approach enables:

- **Rapid Development**: Fast iteration with direct function calls
- **Simple Deployment**: Single container deployment and management
- **Clear Boundaries**: Modules designed for easy future extraction
- **Migration Ready**: Architecture supports service-by-service migration

**For detailed architecture information, see [System Architecture Documentation](./docs/System_Architecture.md).**

## 🛠️ Technology Stack

BA Copilot AI is built on a modern, robust technology stack designed for scalability, maintainability, and developer productivity.

### Core Technologies

| Layer        | Technology                     | Purpose                                  |
| ------------ | ------------------------------ | ---------------------------------------- |
| **Frontend** | NextJS + ReactJS + TailwindCSS | User interface and client-side rendering |
| **Backend**  | Python FastAPI                 | High-performance API framework           |
| **Testing**  | PyTest                         | Versatile, excellent for API testing     |
| **AI/ML**    | LangChain + LangGraph          | LLM orchestration and AI workflows       |
| **Database** | PostgreSQL 14+                 | Primary data storage and persistence     |
| **Cache**    | Redis 6.2+                     | Session storage and caching layer        |

### Development & Operations

| Component            | Technology                      | Purpose                              |
| -------------------- | ------------------------------- | ------------------------------------ |
| **Containerization** | Docker                          | Application packaging and deployment |
| **Orchestration**    | Docker Compose                  | Local development environment        |
| **CI/CD**            | GitHub Actions                  | Automated testing and deployment     |
| **Code Quality**     | Pre-commit hooks, Black, Flake8 | Code formatting and linting          |
| **Testing**          | Pytest + Coverage               | Unit and integration testing         |

### External Services & APIs

| Service                | Provider               | Purpose                       |
| ---------------------- | ---------------------- | ----------------------------- |
| **AI Models**          | OpenAI GPT-4, Claude-3 | Natural language processing   |
| **Documentation**      | Google Docs            | Collaborative documentation   |
| **Communication**      | Google Meet            | Team collaboration            |
| **Project Management** | Google Sheets          | Project tracking and planning |

### Repository Structure

**This is the AI Services Repository** - one of three repositories in the BA Copilot ecosystem:

1. **Frontend Repository**: NextJS + ReactJS + TailwindCSS user interface
2. **Backend Repository**: Core business logic and database operations
3. **AI Services Repository** (This repo): AI-powered services

### Key Design Decisions

- **Docker over Kubernetes**: Simplified deployment without orchestration complexity
- **Modular Monolith**: Fast development with clear microservice migration paths
- **Multi-LLM Support**: Provider flexibility and fallback capabilities
- **PostgreSQL**: ACID compliance and complex query support
- **FastAPI**: High performance with automatic API documentation

## 📁 Project Structure

Our project follows a modular monolith architecture with clear service boundaries:

```
ba_copilot_ai/
├── app/                                # Main application package
│   ├── main.py                         # FastAPI application entry
│   ├── core/                           # Core components (auth, db, security)
│   ├── api/                            # API routes and dependencies
│   ├── models/                         # Database models
│   ├── schemas/                        # Pydantic schemas for API
│   ├── services/                       # Business logic modules
│   ├── repositories/                   # Data access layer
│   └── utils/                          # Utility functions
│
├── tests/                              # Test suites
├── alembic/                            # Database migrations
├── docs/                               # Documentation
├── scripts/                            # Utility scripts
├── Dockerfile                          # Container configuration
├── docker-compose.yml                  # Local development setup
└── pyproject.toml                      # Python project configuration
```

**For detailed project structure information, see [Project Structure Documentation](./docs/project_structure.md).**

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.11 or higher
- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher
- **PostgreSQL**: 14 or higher (or use Docker)
- **Redis**: 6.2 or higher (or use Docker)

### Quick Start with Docker

1. **Clone the repository**:

   ```bash
   git clone git@github.com:KHTNK22-DATN-BA-Copilot/ba_copilot_ai.git
   cd ba_copilot_ai
   ```

2. **Set up environment variables**:

   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

3. **Start the services**:

   ```bash
   # For Docker development
   docker-compose -f infrastructure/docker-compose.yml up -d
   ```

4. **Start the FastAPI server**:

   ```bash
   # Activate virtual environment first
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/macOS

   # Start the server
   cd src
   python main.py
   ```

   Or if you want to have auto-reload (usually for development)

   ```powershell
   cd src
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API**:
   - API Base URL: http://localhost:8000
   - Interactive API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/v1/health/

### Local Development Setup

1. **Create virtual environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:

   ```bash
   # Copy environment template
   cp infrastructure/.env.template .env

   # Edit .env file with your settings
   # Basic setup only requires default values
   ```

4. **Start development services**:

   ```bash
   # Option 1: Start FastAPI server directly (Recommended for AI services)
   cd src
   python main.py

   # Option 2: Using uvicorn with auto-reload
   cd src
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

   # Option 3: Using Docker Compose (if database services needed)
   cd infrastructure
   docker-compose up -d
   ```

5. **Run tests**:

   ```bash
   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=src --cov-report=html

   # Run specific test files
   pytest tests/test_health.py        # Health check tests
   pytest tests/test_srs.py          # SRS generation tests (including POST /srs/generate)
   pytest tests/test_wireframes.py   # Wireframe generation tests
   pytest tests/test_diagrams.py     # Diagram generation tests
   pytest tests/test_conversations.py # AI conversation tests

   # Run only SRS generation endpoint tests
   pytest tests/test_srs.py -k "generate" -v
   ```

### Dependencies Installation Guide

The project uses the following core dependencies:

**Web Framework & API:**

- `fastapi==0.104.1` - Modern, fast web framework for building APIs
- `uvicorn[standard]==0.24.0` - ASGI server for running FastAPI

**Data Validation:**

- `pydantic==2.5.0` - Data validation using Python type annotations
- `pydantic-settings==2.1.0` - Settings management

**Testing Framework:**

- `pytest==7.4.3` - Testing framework
- `pytest-asyncio==0.21.1` - Async testing support
- `pytest-cov==4.1.0` - Coverage reporting
- `httpx==0.25.2` - HTTP client for FastAPI testing

**Development Tools:**

- `black==23.11.0` - Code formatting
- `flake8==6.1.0` - Code linting
- `isort==5.12.0` - Import sorting
- `mypy==1.7.1` - Static type checking

**Virtual Environment Setup:**

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
pip list

# Run application
cd src
python -m uvicorn main:app --reload
```

**Docker Setup (Alternative):**

```bash
# Build and run with Docker Compose
cd infrastructure
docker-compose up --build

# Or build manually
docker build -f infrastructure/Dockerfile -t ba-copilot-ai .
docker run -p 8000:8000 ba-copilot-ai
```

### Configuration

Key environment variables (see `.env.template` for complete list):

| Variable            | Description                  | Default                                      |
| ------------------- | ---------------------------- | -------------------------------------------- |
| `DATABASE_URL`      | PostgreSQL connection string | `postgresql://user:pass@localhost/bacopilot` |
| `REDIS_URL`         | Redis connection string      | `redis://localhost:6379/0`                   |
| `SECRET_KEY`        | JWT signing secret           | `your-secret-key-here`                       |
| `GOOGLE_AI_API_KEY` | Google AI API key            | Required for AI features                     |
| `CLAUDE_API_KEY`    | Anthropic Claude API key     | Optional                                     |
| `LOG_LEVEL`         | Logging level                | `INFO`                                       |
| `ENVIRONMENT`       | Runtime environment          | `development`                                |

## 📚 API Documentation

### Base URL

- **Development**: `http://localhost:8000/v1`
- **Production**: `https://api.bacopilot.com/v1`

### Authentication

All API endpoints require JWT authentication:

```bash
curl -H "Authorization: Bearer <your-jwt-token>" \
     -H "Content-Type: application/json" \
     https://api.bacopilot.com/v1/srs/generate
```

### Core Endpoints

#### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - User authentication
- `POST /auth/refresh` - Refresh access token

#### SRS Generator

- `POST /srs/generate` - Generate SRS document
- `GET /srs/{document_id}` - Retrieve SRS document
- `PUT /srs/{document_id}` - Update SRS document
- `GET /srs/{document_id}/export` - Export SRS document

#### Diagram Generator

- `POST /diagrams/sequence/generate` - Generate sequence diagrams
- `POST /diagrams/architecture/generate` - Generate architecture diagrams
- `POST /diagrams/usecase/generate` - Generate use case diagrams
- `POST /diagrams/flowchart/generate` - Generate flowcharts
- `GET /diagrams/{diagram_id}` - Retrieve diagram
- `GET /diagrams/{diagram_id}/export` - Export diagram

#### Wireframe Generator

- `POST /wireframe/generate` - Generate wireframe
- `GET /wireframe/{wireframe_id}` - Retrieve wireframe
- `PUT /wireframe/{wireframe_id}` - Update wireframe
- `GET /wireframe/{wireframe_id}/export` - Export wireframe

#### AI Conversations

- `POST /conversations` - Create new conversation
- `POST /conversations/{id}/messages` - Send message
- `GET /conversations/{id}` - Get conversation history
- `GET /conversations` - List user conversations

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

**For comprehensive API specification, see [AI API Documentation](./docs/ai_api_specs.md).**

## 🛠️ Development

### Development Commands

Use the provided Makefile for common development tasks:

```bash
# Setup development environment
make setup

# Run tests
make test

# Run tests with coverage
make test-coverage

# Format code
make format

# Lint code
make lint

# Run type checking
make type-check

# Start development server
make dev

# Build Docker images
make build

# Run migrations
make migrate

# Generate migration
make migration name="add_new_table"
```

### Testing

The project includes comprehensive test coverage:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test categories (examples)
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest tests/e2e/           # End-to-end tests

# Run tests with markers (examples)
pytest -m "not slow"        # Skip slow tests
pytest -m "integration"     # Run only integration tests
```

## 🚢 Deployment

### Production Deployment

#### Render Hosting (Recommended)

**BA Copilot AI Services** is optimized for deployment on Render with Docker support:

1. **Quick Deploy to Render:**

   - Connect your GitHub repository to Render
   - Service Type: **Web Service**
   - Language: **Docker**
   - Dockerfile Path: `infrastructure/Dockerfile`
   - Leave Build Command and Start Command empty (auto-detected)

2. **Required Environment Variables:**

   ```bash
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=your-postgresql-url
   REDIS_URL=your-redis-url
   ```

3. **Health Check Path:** `/v1/health/`

📋 **Complete Render deployment guide:** [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)

#### Using Docker Compose (Local Production Testing)

```bash
# Production deployment testing
docker-compose -f infrastructure/docker-compose.prod.yml up -d

# View logs
docker-compose -f infrastructure/docker-compose.prod.yml logs -f

# Stop services
docker-compose -f infrastructure/docker-compose.prod.yml down
```

#### Docker Build & Deploy

```bash
# Build production image
docker build -f infrastructure/Dockerfile -t ba-copilot-ai:latest .

# Run production container
docker run -d \
  --name ba-copilot-ai \
  -p 8000:8000 \
  --env-file .env \
  ba-copilot-ai:latest

# Check health
curl http://localhost:8000/v1/health/
```

### Deployment Verification

After deployment, verify these endpoints:

```bash
# Health check
curl https://your-app.onrender.com/v1/health/

# API documentation (if DEBUG=true)
curl https://your-app.onrender.com/docs

# SRS generation endpoint
curl -X POST https://your-app.onrender.com/v1/srs/generate \
  -H "Content-Type: application/json" \
  -d '{"project_name": "Test Project", "description": "Test SRS generation"}'
```

## 📖 Documentation

### Architecture & Design

- [System Architecture](./docs/System_Architecture.md) - Complete system design and component interactions
- [AI API Specification](./docs/ai_api_specs.md) - REST API documentation for AI services
- [Project Structure](./docs/project_structure.md) - Detailed project organization

### Service Flow Diagrams

- [SRS Generator Flow](./docs/srs_generator_flow.md) - SRS generation process and architecture
- [Wireframe Generator Flow](./docs/wireframe_generator_flow.md) - Wireframe creation workflow
- [AI Conversation Flow](./docs/ai_conversation_flow.md) - Chat system and context management

### Diagram Generation Workflows

- [Sequence Diagram Flow](./docs/sequence_diagram_flow.md) - Sequence diagram generation process and actor identification
- [Architecture Diagram Flow](./docs/architecture_diagram_flow.md) - System architecture diagram creation and component mapping
- [Use Case Diagram Flow](./docs/usecase_diagram_flow.md) - Use case diagram generation and relationship modeling
- [Flowchart Generation Flow](./docs/flowchart_generation_flow.md) - Process flowchart creation and workflow visualization

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/KHTNK22-DATN-BA-Copilot/ba_copilot_ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/KHTNK22-DATN-BA-Copilot/ba_copilot_ai/discussions)
- **Documentation**: [Wiki](https://github.com/KHTNK22-DATN-BA-Copilot/ba_copilot_ai/wiki)

## ⚖️ License

This project is licensed under the [MIT License](./LICENSE). See the LICENSE file for details.

---

**Built with ❤️ by the BA Copilot Team**
