# Project Structure

This document outlines the comprehensive project structure for the BA Copilot AI Core Services backend.

## Directory Structure

```
ba_copilot_ai/
├── src/                                 # Source code
│   ├── api/                            # API Gateway and routing
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI application entry point
│   │   ├── middleware/                 # Custom middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 # Authentication middleware
│   │   │   ├── rate_limit.py           # Rate limiting middleware
│   │   │   ├── cors.py                 # CORS middleware
│   │   │   └── logging.py              # Request logging middleware
│   │   ├── routes/                     # API route definitions
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 # Authentication routes
│   │   │   ├── srs.py                  # SRS generation routes
│   │   │   ├── wireframe.py            # Wireframe generation routes
│   │   │   ├── conversations.py        # AI conversation routes
│   │   │   ├── users.py                # User management routes
│   │   │   └── health.py               # Health check routes
│   │   └── dependencies.py             # FastAPI dependencies
│   │
│   ├── services/                       # Core business services
│   │   ├── __init__.py
│   │   ├── srs_generator/              # SRS Generation Service
│   │   │   ├── __init__.py
│   │   │   ├── service.py              # Main service logic
│   │   │   ├── models.py               # Pydantic models
│   │   │   ├── templates/              # SRS templates
│   │   │   │   ├── standard.py
│   │   │   │   ├── agile.py
│   │   │   │   └── enterprise.py
│   │   │   ├── processors/             # Content processors
│   │   │   │   ├── __init__.py
│   │   │   │   ├── markdown_parser.py
│   │   │   │   ├── requirements_extractor.py
│   │   │   │   └── content_validator.py
│   │   │   └── exporters/              # Document exporters
│   │   │       ├── __init__.py
│   │   │       ├── pdf_exporter.py
│   │   │       ├── markdown_exporter.py
│   │   │       └── html_exporter.py
│   │   │
│   │   ├── wireframe_generator/        # Wireframe Generation Service
│   │   │   ├── __init__.py
│   │   │   ├── service.py              # Main service logic
│   │   │   ├── models.py               # Pydantic models
│   │   │   ├── nlp/                    # Natural Language Processing
│   │   │   │   ├── __init__.py
│   │   │   │   ├── component_extractor.py
│   │   │   │   ├── layout_analyzer.py
│   │   │   │   └── ui_classifier.py
│   │   │   ├── templates/              # Wireframe templates
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── form.py
│   │   │   │   ├── landing.py
│   │   │   │   └── admin.py
│   │   │   ├── generators/             # Code generators
│   │   │   │   ├── __init__.py
│   │   │   │   ├── html_generator.py
│   │   │   │   ├── css_generator.py
│   │   │   │   └── interactive_generator.py
│   │   │   └── exporters/              # Export handlers
│   │   │       ├── __init__.py
│   │   │       ├── figma_exporter.py
│   │   │       ├── sketch_exporter.py
│   │   │       └── html_exporter.py
│   │   │
│   │   ├── conversation_manager/       # AI Conversation Service
│   │   │   ├── __init__.py
│   │   │   ├── service.py              # Main service logic
│   │   │   ├── models.py               # Pydantic models
│   │   │   ├── websocket/              # WebSocket handlers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── connection_manager.py
│   │   │   │   ├── message_handler.py
│   │   │   │   └── session_manager.py
│   │   │   ├── context/                # Context management
│   │   │   │   ├── __init__.py
│   │   │   │   ├── context_manager.py
│   │   │   │   ├── history_compressor.py
│   │   │   │   └── context_validator.py
│   │   │   ├── llm_integration/        # LLM integrations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py
│   │   │   │   ├── openai_client.py
│   │   │   │   ├── claude_client.py
│   │   │   │   └── local_model_client.py
│   │   │   └── analytics/              # Conversation analytics
│   │   │       ├── __init__.py
│   │   │       ├── metrics_collector.py
│   │   │       ├── sentiment_analyzer.py
│   │   │       └── topic_classifier.py
│   │   │
│   │   ├── user_management/            # User Management Service
│   │   │   ├── __init__.py
│   │   │   ├── service.py              # Main service logic
│   │   │   ├── models.py               # Pydantic models
│   │   │   ├── auth/                   # Authentication logic
│   │   │   │   ├── __init__.py
│   │   │   │   ├── jwt_handler.py
│   │   │   │   ├── password_handler.py
│   │   │   │   └── oauth_handler.py
│   │   │   ├── profile/                # User profile management
│   │   │   │   ├── __init__.py
│   │   │   │   ├── profile_manager.py
│   │   │   │   └── preferences_manager.py
│   │   │   └── analytics/              # User analytics
│   │   │       ├── __init__.py
│   │   │       ├── usage_tracker.py
│   │   │       └── behavior_analyzer.py
│   │   │
│   │   └── llm_orchestrator/           # LLM Orchestration Service
│   │       ├── __init__.py
│   │       ├── orchestrator.py         # Main orchestrator
│   │       ├── models.py               # Pydantic models
│   │       ├── providers/              # LLM providers
│   │       │   ├── __init__.py
│   │       │   ├── base_provider.py
│   │       │   ├── openai_provider.py
│   │       │   ├── claude_provider.py
│   │       │   └── local_provider.py
│   │       ├── routing/                # Request routing
│   │       │   ├── __init__.py
│   │       │   ├── router.py
│   │       │   ├── classifier.py
│   │       │   └── load_balancer.py
│   │       └── monitoring/             # LLM monitoring
│   │           ├── __init__.py
│   │           ├── cost_tracker.py
│   │           ├── performance_monitor.py
│   │           └── usage_analyzer.py
│   │
│   ├── shared/                         # Shared utilities and components
│   │   ├── __init__.py
│   │   ├── database/                   # Database utilities
│   │   │   ├── __init__.py
│   │   │   ├── connection.py           # Database connection management
│   │   │   ├── models.py               # SQLAlchemy models
│   │   │   ├── migrations/             # Database migrations
│   │   │   │   └── alembic/
│   │   │   └── repositories/           # Data access layer
│   │   │       ├── __init__.py
│   │   │       ├── base_repository.py
│   │   │       ├── user_repository.py
│   │   │       ├── document_repository.py
│   │   │       ├── wireframe_repository.py
│   │   │       └── conversation_repository.py
│   │   │
│   │   ├── cache/                      # Caching utilities
│   │   │   ├── __init__.py
│   │   │   ├── redis_client.py
│   │   │   ├── cache_manager.py
│   │   │   └── cache_decorators.py
│   │   │
│   │   ├── storage/                    # File storage utilities
│   │   │   ├── __init__.py
│   │   │   ├── s3_client.py
│   │   │   ├── local_storage.py
│   │   │   └── file_manager.py
│   │   │
│   │   ├── messaging/                  # Message queue utilities
│   │   │   ├── __init__.py
│   │   │   ├── rabbitmq_client.py
│   │   │   ├── kafka_client.py
│   │   │   ├── publisher.py
│   │   │   └── consumer.py
│   │   │
│   │   ├── security/                   # Security utilities
│   │   │   ├── __init__.py
│   │   │   ├── encryption.py
│   │   │   ├── jwt_utils.py
│   │   │   ├── rate_limiter.py
│   │   │   └── input_validator.py
│   │   │
│   │   ├── monitoring/                 # Monitoring and logging
│   │   │   ├── __init__.py
│   │   │   ├── logger.py
│   │   │   ├── metrics.py
│   │   │   ├── tracer.py
│   │   │   └── health_checker.py
│   │   │
│   │   ├── exceptions/                 # Custom exceptions
│   │   │   ├── __init__.py
│   │   │   ├── base_exceptions.py
│   │   │   ├── auth_exceptions.py
│   │   │   ├── service_exceptions.py
│   │   │   └── validation_exceptions.py
│   │   │
│   │   └── utils/                      # Utility functions
│   │       ├── __init__.py
│   │       ├── config.py               # Configuration management
│   │       ├── validators.py           # Input validators
│   │       ├── formatters.py           # Data formatters
│   │       ├── helpers.py              # Helper functions
│   │       └── constants.py            # Application constants
│   │
│   └── workers/                        # Background workers
│       ├── __init__.py
│       ├── document_processor.py       # Document processing worker
│       ├── notification_sender.py      # Notification worker
│       ├── analytics_collector.py      # Analytics worker
│       └── cleanup_worker.py           # Cleanup and maintenance worker
│
├── tests/                              # Test suites
│   ├── __init__.py
│   ├── conftest.py                     # Pytest configuration
│   ├── unit/                           # Unit tests
│   │   ├── __init__.py
│   │   ├── services/                   # Service unit tests
│   │   │   ├── test_srs_generator.py
│   │   │   ├── test_wireframe_generator.py
│   │   │   ├── test_conversation_manager.py
│   │   │   └── test_user_management.py
│   │   ├── shared/                     # Shared component tests
│   │   │   ├── test_database.py
│   │   │   ├── test_cache.py
│   │   │   ├── test_storage.py
│   │   │   └── test_security.py
│   │   └── utils/                      # Utility tests
│   │       ├── test_validators.py
│   │       └── test_helpers.py
│   │
│   ├── integration/                    # Integration tests
│   │   ├── __init__.py
│   │   ├── test_api_endpoints.py
│   │   ├── test_database_integration.py
│   │   ├── test_cache_integration.py
│   │   └── test_llm_integration.py
│   │
│   ├── e2e/                           # End-to-end tests
│   │   ├── __init__.py
│   │   ├── test_srs_generation_flow.py
│   │   ├── test_wireframe_generation_flow.py
│   │   └── test_conversation_flow.py
│   │
│   ├── fixtures/                      # Test fixtures and data
│   │   ├── __init__.py
│   │   ├── sample_documents.py
│   │   ├── sample_wireframes.py
│   │   └── sample_conversations.py
│   │
│   └── mocks/                         # Mock objects
│       ├── __init__.py
│       ├── mock_llm_providers.py
│       ├── mock_database.py
│       └── mock_external_services.py
│
├── infrastructure/                     # Infrastructure and deployment
│   ├── docker/                        # Docker configurations
│   │   ├── Dockerfile.api             # API service Docker file
│   │   ├── Dockerfile.worker          # Worker service Docker file
│   │   └── docker-compose.yml         # Local development setup
│   │
│   ├── kubernetes/                    # Kubernetes manifests
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── ingress.yaml
│   │   └── hpa.yaml                   # Horizontal Pod Autoscaler
│   │
│   ├── terraform/                     # Infrastructure as Code
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── modules/
│   │   │   ├── database/
│   │   │   ├── cache/
│   │   │   ├── storage/
│   │   │   └── monitoring/
│   │   └── environments/
│   │       ├── development/
│   │       ├── staging/
│   │       └── production/
│   │
│   └── monitoring/                    # Monitoring configurations
│       ├── prometheus/
│       │   ├── prometheus.yml
│       │   └── rules/
│       ├── grafana/
│       │   ├── dashboards/
│       │   └── datasources/
│       └── alerting/
│           ├── alertmanager.yml
│           └── notification_templates/
│
├── scripts/                           # Utility scripts
│   ├── setup_dev_environment.sh       # Development setup
│   ├── run_migrations.py             # Database migration runner
│   ├── populate_test_data.py         # Test data populator
│   ├── backup_database.sh            # Database backup
│   ├── deploy.sh                     # Deployment script
│   └── health_check.py               # Health check script
│
├── docs/                             # Documentation
│   ├── api/                          # API documentation
│   │   ├── openapi.json              # OpenAPI specification
│   │   └── postman_collection.json   # Postman collection
│   ├── deployment/                   # Deployment guides
│   │   ├── local_development.md
│   │   ├── staging_deployment.md
│   │   └── production_deployment.md
│   ├── architecture/                 # Architecture documentation
│   │   ├── system_design.md
│   │   ├── database_schema.md
│   │   └── api_design.md
│   └── guides/                       # User and developer guides
│       ├── contributing.md
│       ├── coding_standards.md
│       └── troubleshooting.md
│
├── config/                           # Configuration files
│   ├── settings/                     # Application settings
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── staging.py
│   │   └── production.py
│   ├── logging/                      # Logging configurations
│   │   ├── development.yaml
│   │   ├── staging.yaml
│   │   └── production.yaml
│   └── templates/                    # Configuration templates
│       ├── .env.template
│       └── config.yaml.template
│
├── .github/                          # GitHub workflows
│   ├── workflows/
│   │   ├── ci.yml                    # Continuous Integration
│   │   ├── cd.yml                    # Continuous Deployment
│   │   ├── security_scan.yml         # Security scanning
│   │   └── dependency_update.yml     # Dependency updates
│   └── templates/
│       ├── bug_report.md
│       ├── feature_request.md
│       └── pull_request_template.md
│
├── requirements/                     # Python dependencies
│   ├── base.txt                      # Base requirements
│   ├── development.txt               # Development requirements
│   ├── testing.txt                   # Testing requirements
│   └── production.txt                # Production requirements
│
├── .env.template                     # Environment variables template
├── .gitignore                        # Git ignore rules
├── .dockerignore                     # Docker ignore rules
├── .pre-commit-config.yaml           # Pre-commit hooks
├── pyproject.toml                    # Python project configuration
├── Makefile                          # Development commands
├── README.md                         # Project documentation
├── CHANGELOG.md                      # Version history
├── LICENSE                           # License file
└── CONTRIBUTING.md                   # Contribution guidelines
```

## Key Design Principles

### 1. **Microservices Architecture**

Each major service (SRS Generator, Wireframe Generator, Conversation Manager) is designed as an independent module that can be developed, tested, and deployed separately.

### 2. **Separation of Concerns**

- **API Layer**: Handles HTTP requests and responses
- **Service Layer**: Contains business logic
- **Data Layer**: Manages data access and persistence
- **Shared Layer**: Provides common utilities and components

### 3. **Domain-Driven Design**

Services are organized around business domains, making the codebase more maintainable and allowing teams to work independently on different features.

### 4. **Testability**

Comprehensive test structure with unit, integration, and end-to-end tests, along with fixtures and mocks for isolated testing.

### 5. **Infrastructure as Code**

All infrastructure components are defined as code, enabling version control, reproducibility, and automated deployments.

### 6. **Configuration Management**

Environment-specific configurations are separated and managed through configuration files and environment variables.

### 7. **Observability**

Built-in monitoring, logging, and tracing capabilities for production observability and debugging.

## Service Organization

### **API Gateway Pattern**

All external requests go through the API gateway (`src/api/`), which handles:

- Authentication and authorization
- Rate limiting
- Request routing
- Response caching
- CORS handling

### **Service Layer Pattern**

Each core service follows a consistent structure:

- `service.py`: Main business logic
- `models.py`: Data models and validation
- Specialized subdirectories for domain-specific functionality
- Clear separation between internal logic and external integrations

### **Shared Components**

Common functionality is extracted into the shared layer:

- Database connections and repositories
- Caching mechanisms
- Security utilities
- Monitoring and logging
- Message queue handling

### **Infrastructure Management**

Infrastructure components are managed through:

- Docker containerization for consistent environments
- Kubernetes manifests for orchestration
- Terraform for infrastructure provisioning
- Monitoring stack for observability

This structure provides:

- **Scalability**: Each service can be scaled independently
- **Maintainability**: Clear separation of concerns and consistent patterns
- **Testability**: Comprehensive test coverage with proper isolation
- **Deployability**: Infrastructure as code with automated CI/CD
- **Observability**: Built-in monitoring and logging capabilities
