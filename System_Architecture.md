# System Architecture - BA Copilot AI Core Services

## Overview

The BA Copilot AI Core Services system is designed as a microservices-based architecture that provides AI-powered tools for Business Analysts. The system emphasizes scalability, maintainability, and high availability while delivering fast and reliable AI services.

## Architecture Principles

- **Microservices Architecture**: Loosely coupled, independently deployable services
- **API-First Design**: Well-defined REST APIs for all inter-service communication
- **Event-Driven Architecture**: Asynchronous processing for long-running operations
- **Cloud-Native**: Designed for containerized deployment and auto-scaling
- **Security by Design**: Zero-trust security model with comprehensive authentication
- **Observability**: Comprehensive logging, monitoring, and distributed tracing

## System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Frontend]
        MOBILE[Mobile App]
        SDK[SDK/Libraries]
    end

    subgraph "API Gateway Layer"
        GATEWAY[API Gateway]
        RATE[Rate Limiter]
        AUTH[Auth Middleware]
        CACHE[Response Cache]
    end

    subgraph "Core Services"
        SRS[SRS Generator Service]
        WIRE[Wireframe Generator]
        CHAT[AI Conversation Service]
        USER[User Management Service]
    end

    subgraph "AI/ML Layer"
        LLM[LLM Orchestrator]
        OPENAI[OpenAI API]
        CLAUDE[Claude API]
        LOCAL[Local Models]
    end

    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        REDIS[(Redis Cache)]
        S3[(Object Storage)]
        VECTOR[(Vector Database)]
    end

    subgraph "Infrastructure"
        QUEUE[Message Queue]
        MONITOR[Monitoring]
        LOGS[Centralized Logging]
        BACKUP[Backup Service]
    end

    WEB --> GATEWAY
    MOBILE --> GATEWAY
    SDK --> GATEWAY

    GATEWAY --> RATE
    RATE --> AUTH
    AUTH --> CACHE
    CACHE --> SRS
    CACHE --> WIRE
    CACHE --> CHAT
    CACHE --> USER

    SRS --> LLM
    WIRE --> LLM
    CHAT --> LLM

    LLM --> OPENAI
    LLM --> CLAUDE
    LLM --> LOCAL

    SRS --> POSTGRES
    WIRE --> S3
    CHAT --> POSTGRES
    USER --> POSTGRES

    SRS --> REDIS
    WIRE --> REDIS
    CHAT --> REDIS
    CHAT --> VECTOR

    SRS --> QUEUE
    WIRE --> QUEUE
    CHAT --> QUEUE

    ALL_SERVICES --> MONITOR
    ALL_SERVICES --> LOGS
```

## Core Components

### 1. API Gateway Layer

#### API Gateway

- **Technology**: Kong, AWS API Gateway, or Traefik
- **Responsibilities**:
  - Request routing and load balancing
  - SSL termination
  - API versioning
  - Request/response transformation
  - Cross-origin resource sharing (CORS)

#### Rate Limiter

- **Technology**: Redis-based rate limiting
- **Features**:
  - Per-user and per-endpoint limits
  - Sliding window algorithm
  - Burst capacity handling
  - Dynamic limit adjustment

#### Authentication Middleware

- **Technology**: JWT with RSA256 signing
- **Features**:
  - Token validation and refresh
  - Role-based access control (RBAC)
  - Session management
  - Multi-factor authentication support

### 2. Core Services Architecture

Each core service follows a consistent internal architecture:

```mermaid
graph TD
    subgraph "Service Internal Architecture"
        API[REST API Layer]
        BIZ[Business Logic Layer]
        DATA[Data Access Layer]
        CACHE[Caching Layer]
        QUEUE[Queue Handler]
    end

    API --> BIZ
    BIZ --> DATA
    BIZ --> CACHE
    BIZ --> QUEUE
    DATA --> DB[(Database)]
    CACHE --> REDIS[(Redis)]
    QUEUE --> MQ[Message Queue]
```

#### SRS Generator Service

- **Technology**: FastAPI + Python
- **Components**:
  - Input validation and preprocessing
  - Template engine for SRS structure
  - LLM integration for content generation
  - Document versioning and storage
  - Export functionality (PDF, HTML, Markdown)

#### Wireframe Generator Service

- **Technology**: FastAPI + Python + Node.js (for HTML/CSS generation)
- **Components**:
  - Natural language processing for UI component extraction
  - Template-based wireframe generation
  - HTML/CSS code generation
  - Interactive preview system
  - Export to design tools (Figma, Sketch)

#### AI Conversation Service

- **Technology**: FastAPI + WebSocket + Python
- **Components**:
  - Real-time WebSocket connections
  - Conversation context management
  - Multi-LLM routing and fallback
  - Message history and search
  - Conversation analytics

#### User Management Service

- **Technology**: FastAPI + Python
- **Components**:
  - User authentication and authorization
  - Profile and preference management
  - Usage tracking and analytics
  - Subscription and billing integration

### 3. AI/ML Layer

#### LLM Orchestrator

```mermaid
graph TD
    REQUEST[Incoming AI Request] --> ROUTER[LLM Router]
    ROUTER --> CLASSIFIER[Request Classifier]

    CLASSIFIER --> |Technical| TECH[Technical LLM Pool]
    CLASSIFIER --> |Creative| CREATIVE[Creative LLM Pool]
    CLASSIFIER --> |General| GENERAL[General LLM Pool]

    TECH --> OPENAI_TECH[OpenAI GPT-4]
    TECH --> CLAUDE_TECH[Claude-3 Opus]

    CREATIVE --> CLAUDE_CREATIVE[Claude-3]
    CREATIVE --> LOCAL_CREATIVE[Local Creative Model]

    GENERAL --> OPENAI_GENERAL[OpenAI GPT-3.5]
    GENERAL --> LOCAL_GENERAL[Local General Model]

    OPENAI_TECH --> RESPONSE[Response Aggregator]
    CLAUDE_TECH --> RESPONSE
    CLAUDE_CREATIVE --> RESPONSE
    LOCAL_CREATIVE --> RESPONSE
    OPENAI_GENERAL --> RESPONSE
    LOCAL_GENERAL --> RESPONSE

    RESPONSE --> CACHE_LAYER[Response Cache]
    CACHE_LAYER --> OUTPUT[Final Response]
```

**Features**:

- Intelligent routing based on request type
- Load balancing across multiple providers
- Fallback mechanisms for high availability
- Response caching for performance
- Cost optimization through provider selection

### 4. Data Layer Architecture

#### Primary Database (PostgreSQL)

```sql
-- Core entities schema
Users
├── user_id (UUID, PK)
├── email (VARCHAR, UNIQUE)
├── password_hash (VARCHAR)
├── full_name (VARCHAR)
├── created_at (TIMESTAMP)
└── preferences (JSONB)

Documents (SRS)
├── document_id (UUID, PK)
├── user_id (UUID, FK)
├── project_name (VARCHAR)
├── content (TEXT)
├── metadata (JSONB)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

Wireframes
├── wireframe_id (UUID, PK)
├── user_id (UUID, FK)
├── html_content (TEXT)
├── css_styles (TEXT)
├── metadata (JSONB)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

Conversations
├── conversation_id (UUID, PK)
├── user_id (UUID, FK)
├── title (VARCHAR)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

Messages
├── message_id (UUID, PK)
├── conversation_id (UUID, FK)
├── role (ENUM: user, assistant)
├── content (TEXT)
├── metadata (JSONB)
└── timestamp (TIMESTAMP)
```

#### Caching Layer (Redis)

- **Session Storage**: User sessions and JWT tokens
- **API Response Cache**: Frequently accessed data
- **Rate Limiting**: Request counters and windows
- **Real-time Data**: WebSocket connection states
- **Queue Management**: Job queues for async processing

#### Object Storage (S3/MinIO)

- **Document Storage**: Generated PDFs, exports
- **Wireframe Assets**: HTML files, CSS, images
- **User Uploads**: Input documents and attachments
- **Backup Storage**: Database backups and archives

#### Vector Database (Pinecone/Weaviate)

- **Conversation Embeddings**: For semantic search
- **Document Similarity**: Template matching
- **User Behavior Vectors**: Recommendation system
- **Knowledge Base**: FAQ and help content

### 5. Message Queue and Event System

```mermaid
graph LR
    subgraph "Event Producers"
        SRS_SERV[SRS Service]
        WIRE_SERV[Wireframe Service]
        CHAT_SERV[Chat Service]
        USER_SERV[User Service]
    end

    subgraph "Message Queue (RabbitMQ/Apache Kafka)"
        TOPIC1[document.generated]
        TOPIC2[wireframe.created]
        TOPIC3[conversation.message]
        TOPIC4[user.action]
    end

    subgraph "Event Consumers"
        NOTIFICATION[Notification Service]
        ANALYTICS[Analytics Service]
        BACKUP[Backup Service]
        WEBHOOK[Webhook Service]
    end

    SRS_SERV --> TOPIC1
    WIRE_SERV --> TOPIC2
    CHAT_SERV --> TOPIC3
    USER_SERV --> TOPIC4

    TOPIC1 --> NOTIFICATION
    TOPIC1 --> ANALYTICS
    TOPIC1 --> BACKUP

    TOPIC2 --> NOTIFICATION
    TOPIC2 --> ANALYTICS
    TOPIC3 --> ANALYTICS
    TOPIC4 --> ANALYTICS

    TOPIC1 --> WEBHOOK
    TOPIC2 --> WEBHOOK
```

### 6. Security Architecture

```mermaid
graph TD
    subgraph "Security Layers"
        WAF[Web Application Firewall]
        TLS[TLS 1.3 Encryption]
        GATEWAY[API Gateway Security]
        AUTH[JWT Authentication]
        RBAC[Role-Based Access Control]
        DATA_ENC[Data Encryption at Rest]
        AUDIT[Audit Logging]
    end

    CLIENT[Client Request] --> WAF
    WAF --> TLS
    TLS --> GATEWAY
    GATEWAY --> AUTH
    AUTH --> RBAC
    RBAC --> SERVICE[Core Services]
    SERVICE --> DATA_ENC
    ALL_LAYERS --> AUDIT
```

**Security Features**:

- End-to-end encryption (TLS 1.3)
- JWT tokens with short expiration
- Role-based access control
- API rate limiting and DDoS protection
- Data encryption at rest (AES-256)
- Comprehensive audit logging
- Regular security scanning and updates

### 7. Deployment Architecture

#### Container Architecture

```mermaid
graph TD
    subgraph "Kubernetes Cluster"
        subgraph "API Gateway Namespace"
            GW_POD[API Gateway Pods]
            INGRESS[Ingress Controller]
        end

        subgraph "Core Services Namespace"
            SRS_PODS[SRS Service Pods]
            WIRE_PODS[Wireframe Service Pods]
            CHAT_PODS[Chat Service Pods]
            USER_PODS[User Service Pods]
        end

        subgraph "Data Namespace"
            PG_CLUSTER[PostgreSQL Cluster]
            REDIS_CLUSTER[Redis Cluster]
            VECTOR_DB[Vector Database]
        end

        subgraph "Infrastructure Namespace"
            MONITORING[Monitoring Stack]
            LOGGING[Logging Stack]
            BACKUP[Backup Jobs]
        end
    end

    subgraph "External Services"
        S3[Object Storage]
        LLM_APIS[LLM Provider APIs]
        CDN[Content Delivery Network]
    end

    INGRESS --> GW_POD
    GW_POD --> SRS_PODS
    GW_POD --> WIRE_PODS
    GW_POD --> CHAT_PODS
    GW_POD --> USER_PODS

    SRS_PODS --> PG_CLUSTER
    WIRE_PODS --> PG_CLUSTER
    CHAT_PODS --> PG_CLUSTER
    USER_PODS --> PG_CLUSTER

    ALL_SERVICES --> REDIS_CLUSTER
    CHAT_PODS --> VECTOR_DB

    ALL_SERVICES --> S3
    ALL_SERVICES --> LLM_APIS
    STATIC_ASSETS --> CDN
```

#### Infrastructure Components

- **Container Orchestration**: Kubernetes
- **Service Mesh**: Istio (optional, for advanced traffic management)
- **Load Balancer**: NGINX Ingress Controller
- **Auto Scaling**: Horizontal Pod Autoscaler (HPA)
- **Persistent Storage**: Kubernetes Persistent Volumes
- **Secret Management**: Kubernetes Secrets + External Secret Operator

### 8. Monitoring and Observability

```mermaid
graph TD
    subgraph "Application Layer"
        APPS[Core Services]
        METRICS[Custom Metrics]
        TRACES[Distributed Traces]
        LOGS[Application Logs]
    end

    subgraph "Collection Layer"
        PROMETHEUS[Prometheus]
        JAEGER[Jaeger]
        FLUENTD[Fluentd]
    end

    subgraph "Storage Layer"
        TSDB[Time Series Database]
        TRACE_STORE[Trace Storage]
        LOG_STORE[Elasticsearch]
    end

    subgraph "Visualization Layer"
        GRAFANA[Grafana Dashboards]
        KIBANA[Kibana Logs]
        ALERTS[AlertManager]
    end

    APPS --> METRICS
    APPS --> TRACES
    APPS --> LOGS

    METRICS --> PROMETHEUS
    TRACES --> JAEGER
    LOGS --> FLUENTD

    PROMETHEUS --> TSDB
    JAEGER --> TRACE_STORE
    FLUENTD --> LOG_STORE

    TSDB --> GRAFANA
    TRACE_STORE --> GRAFANA
    LOG_STORE --> KIBANA

    PROMETHEUS --> ALERTS
    ALERTS --> NOTIFICATION[Slack/Email/PagerDuty]
```

**Key Metrics**:

- API response times and error rates
- LLM service latency and costs
- Database connection pools and query performance
- Cache hit rates and memory usage
- User activity and feature adoption
- Infrastructure resource utilization

### 9. Disaster Recovery and Backup

#### Backup Strategy

```mermaid
graph TD
    subgraph "Data Sources"
        PG[PostgreSQL]
        REDIS[Redis]
        S3_DATA[Object Storage]
        CONFIG[Configuration]
    end

    subgraph "Backup Types"
        FULL[Full Backup]
        INCREMENTAL[Incremental Backup]
        POINT_IN_TIME[Point-in-Time Recovery]
        SNAPSHOT[Volume Snapshots]
    end

    subgraph "Backup Storage"
        S3_BACKUP[S3 Backup Bucket]
        GLACIER[Glacier Archive]
        OFFSITE[Offsite Backup]
    end

    PG --> FULL
    PG --> INCREMENTAL
    PG --> POINT_IN_TIME
    S3_DATA --> SNAPSHOT
    REDIS --> SNAPSHOT
    CONFIG --> FULL

    FULL --> S3_BACKUP
    INCREMENTAL --> S3_BACKUP
    POINT_IN_TIME --> S3_BACKUP
    SNAPSHOT --> S3_BACKUP

    S3_BACKUP --> GLACIER
    S3_BACKUP --> OFFSITE
```

**Recovery Time Objectives (RTO)**:

- Critical Services: < 15 minutes
- Database Recovery: < 30 minutes
- Full System Recovery: < 2 hours

**Recovery Point Objectives (RPO)**:

- Transactional Data: < 5 minutes
- User-generated Content: < 15 minutes
- Configuration Changes: < 1 hour

### 10. Performance and Scalability

#### Horizontal Scaling Strategy

- **Auto-scaling**: Based on CPU, memory, and custom metrics
- **Load Distribution**: Round-robin with health checks
- **Database Scaling**: Read replicas and connection pooling
- **Cache Scaling**: Redis Cluster with consistent hashing
- **CDN Integration**: Static asset distribution

#### Performance Targets

- API Response Time: P95 < 200ms, P99 < 500ms
- AI Service Response: P95 < 3s, P99 < 10s
- Database Query Time: P95 < 50ms
- Cache Hit Rate: > 80%
- System Availability: 99.9% uptime

### 11. Development and Deployment Pipeline

```mermaid
graph LR
    subgraph "Development"
        DEV[Local Development]
        TEST[Unit Tests]
        LINT[Code Quality]
    end

    subgraph "CI/CD Pipeline"
        BUILD[Build Image]
        SECURITY[Security Scan]
        INTEGRATION[Integration Tests]
        STAGING[Staging Deploy]
        PROD[Production Deploy]
    end

    subgraph "Environments"
        DEV_ENV[Development]
        STAGING_ENV[Staging]
        PROD_ENV[Production]
    end

    DEV --> TEST
    TEST --> LINT
    LINT --> BUILD
    BUILD --> SECURITY
    SECURITY --> INTEGRATION
    INTEGRATION --> STAGING
    STAGING --> PROD

    STAGING --> STAGING_ENV
    PROD --> PROD_ENV
```

**Pipeline Features**:

- Automated testing and quality gates
- Container security scanning
- Blue-green deployment strategy
- Automated rollback on failure
- Feature flags for gradual rollouts

## Technology Stack Summary

| Component              | Technology            | Purpose                               |
| ---------------------- | --------------------- | ------------------------------------- |
| **API Framework**      | FastAPI               | High-performance Python web framework |
| **Database**           | PostgreSQL 14+        | Primary data storage                  |
| **Cache**              | Redis 6+              | Session storage and caching           |
| **Message Queue**      | RabbitMQ/Apache Kafka | Asynchronous processing               |
| **Object Storage**     | MinIO/AWS S3          | File and document storage             |
| **Vector Database**    | Pinecone/Weaviate     | Semantic search and embeddings        |
| **Container Platform** | Docker + Kubernetes   | Container orchestration               |
| **API Gateway**        | Kong/Traefik          | API routing and management            |
| **Monitoring**         | Prometheus + Grafana  | Metrics and visualization             |
| **Logging**            | ELK Stack             | Centralized logging                   |
| **Tracing**            | Jaeger                | Distributed tracing                   |
| **Security**           | JWT + OAuth2          | Authentication and authorization      |
| **CI/CD**              | GitHub Actions        | Automated deployment pipeline         |

## Future Enhancements

1. **Machine Learning Pipeline**: Custom model training and deployment
2. **GraphQL API**: Alternative API interface for complex queries
3. **Multi-tenant Architecture**: Support for enterprise customers
4. **Advanced Analytics**: Business intelligence and reporting
5. **Mobile SDK**: Native mobile application support
6. **Plugin System**: Third-party integrations and extensions
7. **Advanced AI Features**: Code generation, automated testing
8. **Compliance Framework**: SOC2, GDPR, HIPAA compliance modules

This architecture provides a solid foundation for the BA Copilot AI Core Services, ensuring scalability, reliability, and maintainability while delivering high-performance AI-powered tools for Business Analysts.
