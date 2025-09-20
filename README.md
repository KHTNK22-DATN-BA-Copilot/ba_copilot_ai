# BA Copilot AI - Core Services Backend

Backend repository for **Business Analyst Copilot Artificial Intelligence** _(BA Copilot)_, providing comprehensive AI-powered services and APIs to support automated artifact creation, intelligent conversations, and workflow optimization for Business Analysts and professionals.

## 🎯 Overview

BA Copilot AI Core Services is a microservices-based backend platform that leverages advanced Large Language Models (LLMs) to automate the creation of business analysis artifacts. The platform provides intelligent tools for generating Software Requirements Specifications (SRS), creating wireframe prototypes, and managing AI-powered conversations.

## 📋 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
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
- **Wireframe Generator**: AI-powered conversion of textual requirements into interactive wireframe prototypes
- **AI Conversation Manager**: Intelligent chat system with context management, multi-LLM routing, and conversation history
- **Document Processing**: Advanced parsing and analysis of business documents in various formats

### 🚀 Technical Features

- **RESTful API Design**: Industry-standard REST APIs with comprehensive OpenAPI documentation
- **Microservices Architecture**: Independently scalable services with clear domain boundaries
- **Multi-LLM Integration**: Support for OpenAI GPT-4, Claude-3, and local models with intelligent routing
- **Real-time Communication**: WebSocket-based real-time chat and streaming responses
- **Authentication & Security**: JWT-based authentication with role-based access control
- **High Performance**: Redis caching, connection pooling, and optimized database queries
- **Monitoring & Observability**: Comprehensive logging, metrics, and distributed tracing

## 🏗️ System Architecture

The system follows a microservices architecture pattern with the following key components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   Mobile App     │    │  SDK/Libraries  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                        ┌─────────▼─────────┐
                        │   API Gateway     │
                        │ (Auth, Rate Limit,│
                        │  Caching, CORS)   │
                        └─────────┬─────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
    ┌─────▼─────┐       ┌─────────▼─────────┐     ┌─────▼─────┐
    │    SRS    │       │    Wireframe      │     │    AI     │
    │ Generator │       │   Generator       │     │Conversation│
    │  Service  │       │    Service        │     │  Manager  │
    └─────┬─────┘       └─────────┬─────────┘     └─────┬─────┘
          │                       │                     │
          └───────────────────────┼─────────────────────┘
                                  │
                        ┌─────────▼─────────┐
                        │ LLM Orchestrator  │
                        │(OpenAI, Claude,   │
                        │ Local Models)     │
                        └─────────┬─────────┘
                                  │
    ┌─────────────────────────────┼─────────────────────────────┐
    │                             │                             │
┌───▼───┐  ┌─────▼─────┐  ┌──────▼──────┐  ┌─────▼─────┐  ┌───▼────┐
│PostgreSQL│ │Redis Cache│  │Object Storage│  │Vector DB │  │Message │
│Database│ │           │  │  (S3/MinIO) │  │(Pinecone)│  │ Queue  │
└─────────┘  └───────────┘  └─────────────┘  └──────────┘  └────────┘
```

### Core Components:

- **API Gateway**: Request routing, authentication, rate limiting
- **SRS Generator**: Document generation from requirements
- **Wireframe Generator**: UI prototype creation from descriptions
- **AI Conversation Manager**: Multi-LLM chat with context management
- **LLM Orchestrator**: Intelligent routing across multiple AI providers
- **Data Layer**: PostgreSQL, Redis, Object Storage, Vector Database

## 📁 Project Structure

Our project follows a domain-driven microservices architecture:

```
ba_copilot_ai/
├── src/                                 # Source code
│   ├── api/                            # API Gateway and routing
│   │   ├── main.py                     # FastAPI application entry
│   │   ├── middleware/                 # Custom middleware
│   │   ├── routes/                     # API route definitions
│   │   └── dependencies.py             # FastAPI dependencies
│   │
│   ├── services/                       # Core business services
│   │   ├── srs_generator/              # SRS Generation Service
│   │   ├── wireframe_generator/        # Wireframe Generation Service
│   │   ├── conversation_manager/       # AI Conversation Service
│   │   ├── user_management/            # User Management Service
│   │   └── llm_orchestrator/           # LLM Orchestration Service
│   │
│   ├── shared/                         # Shared utilities and components
│   │   ├── database/                   # Database utilities
│   │   ├── cache/                      # Caching utilities
│   │   ├── storage/                    # File storage utilities
│   │   ├── messaging/                  # Message queue utilities
│   │   ├── security/                   # Security utilities
│   │   └── monitoring/                 # Monitoring and logging
│   │
│   └── workers/                        # Background workers
│
├── tests/                              # Test suites
│   ├── unit/                           # Unit tests
│   ├── integration/                    # Integration tests
│   ├── e2e/                           # End-to-end tests
│   └── fixtures/                      # Test fixtures and data
│
├── infrastructure/                     # Infrastructure and deployment
│   ├── docker/                        # Docker configurations
│   ├── kubernetes/                    # Kubernetes manifests
│   ├── terraform/                     # Infrastructure as Code
│   └── monitoring/                    # Monitoring configurations
│
└── docs/                             # Documentation
    ├── api/                          # API documentation
    ├── architecture/                 # Architecture documentation
    └── guides/                       # User and developer guides
```

For detailed project structure information, see [Project Structure Documentation](./docs/project_structure.md).

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
   docker-compose up -d
   ```

4. **Run database migrations**:

   ```bash
   docker-compose exec api python scripts/run_migrations.py
   ```

5. **Access the API**:
   - API Base URL: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Local Development Setup

1. **Create virtual environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements/development.txt
   ```

3. **Set up pre-commit hooks**:

   ```bash
   pre-commit install
   ```

4. **Start development services**:

   ```bash
   # Start PostgreSQL and Redis
   docker-compose up -d postgres redis

   # Run the API server
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Configuration

Key environment variables (see `.env.template` for complete list):

| Variable         | Description                  | Default                                      |
| ---------------- | ---------------------------- | -------------------------------------------- |
| `DATABASE_URL`   | PostgreSQL connection string | `postgresql://user:pass@localhost/bacopilot` |
| `REDIS_URL`      | Redis connection string      | `redis://localhost:6379/0`                   |
| `SECRET_KEY`     | JWT signing secret           | `your-secret-key-here`                       |
| `OPENAI_API_KEY` | OpenAI API key               | Required for AI features                     |
| `CLAUDE_API_KEY` | Anthropic Claude API key     | Optional                                     |
| `LOG_LEVEL`      | Logging level                | `INFO`                                       |
| `ENVIRONMENT`    | Runtime environment          | `development`                                |

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

For detailed API specification, see [API Documentation](./API_Specification.md).

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

#### Using Docker Compose (Simple Deployment)

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## 📖 Documentation

### Architecture & Design

- [System Architecture](./System_Architecture.md) - Complete system design and component interactions
- [API Specification](./API_Specification.md) - Comprehensive REST API documentation
- [Project Structure](./docs/project_structure.md) - Detailed project organization

### Service Flow Diagrams

- [SRS Generator Flow](./docs/srs_generator_flow.md) - SRS generation process and architecture
- [Wireframe Generator Flow](./docs/wireframe_generator_flow.md) - Wireframe creation workflow
- [AI Conversation Flow](./docs/ai_conversation_flow.md) - Chat system and context management

### Development Guides

- [Local Development Setup](./docs/deployment/local_development.md)
- [Contributing Guidelines](./CONTRIBUTING.md)
- [Coding Standards](./docs/guides/coding_standards.md)
- [Troubleshooting Guide](./docs/guides/troubleshooting.md)

### Deployment & Operations

- [Production Deployment](./docs/deployment/production_deployment.md)
- [Monitoring & Observability](./docs/architecture/monitoring.md)
- [Security Guidelines](./docs/guides/security.md)

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/KHTNK22-DATN-BA-Copilot/ba_copilot_ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/KHTNK22-DATN-BA-Copilot/ba_copilot_ai/discussions)
- **Documentation**: [Wiki](https://github.com/KHTNK22-DATN-BA-Copilot/ba_copilot_ai/wiki)

## ⚖️ License

This project is licensed under the [MIT License](./LICENSE). See the LICENSE file for details.

---

**Built with ❤️ by the BA Copilot Team**
