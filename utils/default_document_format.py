class DocumentFormat:
    SRS = """
# Software Requirements Specification (SRS
> Standard: ISO/IEC/IEEE 29148 (IEEE SRS)
---
# 1. Introduction
## 1.1 Purpose
## 1.2 Scope
## 1.3 Intended Audience
## 1.4 References
---
# 2. Overall Description
## 2.1 Product Perspective
## 2.2 Product Functions
## 2.3 User Classes
## 2.4 Operating Environment
## 2.5 Constraints
## 2.6 Assumptions and Dependencies
---
# 3. External Interface Requirements
## 3.1 User Interfaces
## 3.2 Hardware Interfaces
## 3.3 Software Interfaces
## 3.4 Communication Interfaces
---
# 4. Functional Requirements
## 4.1 <Feature Name>
### Description
### Priority
### Preconditions
### Postconditions
### Functional Requirements
| ID | Requirement |
|----|-------------|
| FR-001 | |
| FR-002 | |
### Acceptance Criteria
---
## 4.2 <Feature Name>
Repeat the same structure for every feature.
---
# 5. Non-Functional Requirements
## 5.1 Performance
## 5.2 Security
## 5.3 Reliability
## 5.4 Availability
## 5.5 Scalability
## 5.6 Maintainability
## 5.7 Usability
## 5.8 Compliance
# 6. Business Rules
# 7. Other Requirements
# Appendix A. Glossary
# Appendix B. Analysis Models
- Use Case Diagram
- Context Diagram
- ERD
- State Diagram
- Activity Diagram
- Sequence Diagram
(Include only applicable diagrams.)
---
# Appendix C. TBD Items
| ID | Description | Status |
|----|-------------|--------|
| TBD-001 | | |
"""
    HLD_ARCH = """
# HIGH-LEVEL ARCHITECTURE DESIGN (HLD - ARCHITECTURE)
| Project / System Name | [Project/System Name] |
| :--- | :--- |
| **Status** | Draft / Under Review / Approved |
| **Author** | [Author Name] |
| **Version** | v1.0.0 |
| **Date** | [YYYY-MM-DD] |
| **Approver(s)**| [Approver Name] |
---
## 1. System Overview
*Provide a concise summary of the system, its context, and the business goals it serves.*
*   **Context & Goals:**
    *   *Keywords:* `Business Goal`, `Problem Statement`, `Success Metrics`.
    *   *Description:* Explain the business or technical problems this architecture addresses and the core goals of the system (e.g., performance, cost optimization, reliability).
*   **Architectural Scope:**
    *   **In Scope:** Define components, interfaces, or systems covered in this design.
    *   **Out of Scope:** Explicitly list related aspects excluded from this architecture to prevent scope creep.
## 2. Logical Architecture
*Illustrate how the system is partitioned into logical layers, services, and modules, and how they interact conceptually.*
*   **Logical Architecture Diagram:**
    *   *Keywords:* `Presentation Layer`, `Application Layer`, `Domain Layer`, `Data Layer`, `Mermaid Diagram`.
    *   *Instruction:* Customize the Mermaid diagram below to visualize your logical structure.
    ```mermaid
    graph TD
        Client[Client: Web/Mobile] --> Gateway[API Gateway / Load Balancer]
        Gateway --> AuthService[Auth Service]
        Gateway --> CoreService[Core Business Service]
        CoreService --> DB[(Database)]
        CoreService --> Queue[Message Queue]
        Queue --> Worker[Background Worker]
    ```
*   **Architectural Style & Design Principles:**
    *   *Keywords:* `Microservices`, `Monolithic`, `Event-Driven`, `Serverless`, `Loosely Coupled`, `Domain-Driven Design`.
    *   *Description:* Detail the chosen architectural pattern and why it fits the business requirements.

## 3. Component Breakdown
*Define the key logical components of the system and their respective responsibilities.*

| Component | Main Responsibilities | Protocol(s) | Technology / Notes |
| :--- | :--- | :--- | :--- |
| **API Gateway** | Routing, rate limiting, SSL termination, request auditing | HTTPS | e.g., Kong, Nginx, APISIX |
| **Auth Service** | User authentication, token issuance, RBAC verification | HTTPS, gRPC | e.g., Keycloak, Custom Auth |
| **Core Service** | Process core business logic and workflows | HTTP/REST, gRPC | Core Application logic |
| **Message Queue** | Asynchronous communication and event ingestion | AMQP / Kafka protocol | e.g., RabbitMQ, Apache Kafka |
| **Database** | Structured and relational data storage | SQL Driver | e.g., PostgreSQL, MySQL |

## 4. Data Flow & Component Interactions
*Describe how components interact to fulfill major business use cases.*

*   **Sequence Diagram:**
    *   *Keywords:* `Interaction Flow`, `Request-Response`, `Lifeline`.
    *   *Instruction:* Modify the Mermaid sequence flow below to match your main system process (e.g., Login, Checkout).
    ```mermaid
    sequenceDiagram
        autonumber
        actor User as End User
        participant FE as Frontend App
        participant GW as API Gateway
        participant Auth as Auth Service
        
        User->>FE: Input Credentials
        FE->>GW: POST /login
        GW->>Auth: Validate Credentials
        Auth-->>GW: Return JWT Token
        GW-->>FE: HTTP 200 OK (Token)
        FE-->>User: Redirect to Dashboard
    ```

## 5. Architectural Non-Functional Requirements (NFRs)
*Document the cross-cutting architectural constraints and metrics.*

*   **High Availability & Redundancy (HA):**
    *   *Keywords:* `Single Point of Failure (SPOF)`, `Multi-AZ Deployment`, `Load Balancing`.
    *   *Description:* Explain how the architecture guarantees high availability and avoids single points of failure.
*   **Scalability:**
    *   *Keywords:* `Horizontal Scaling`, `Vertical Scaling`, `Stateless Components`.
    *   *Description:* Explain the scaling strategy (e.g., auto-scaling stateless application nodes based on CPU utilization).

## 6. Architectural Decision Records (ADR)
*Log significant architectural choices and the trade-offs considered.*

### ADR 001: Choice of Communication Protocol between Services
*   **Status:** Approved / Proposed / Rejected
*   **Context:** We need a low-latency, strongly-typed communication protocol for internal microservice-to-microservice traffic.
*   **Decision:** We will use **gRPC** instead of **REST over HTTP/1.1** for internal service-to-service communication.
*   **Consequences:** Improved performance and payload compression, schema enforcement via Protobuf, but increased complexity in debugging and testing.
"""
    HLD_CLOUD = """
# HIGH-LEVEL CLOUD INFRASTRUCTURE DESIGN (HLD - CLOUD INFRASTRUCTURE)

| Project / System Name | [Project/System Name] |
| :--- | :--- |
| **Status** | Draft / Under Review / Approved |
| **Author** | [Cloud Architect / DevOps Engineer] |
| **Cloud Provider** | AWS / Azure / GCP / Hybrid / On-Prem |
| **Version** | v1.0.0 |
| **Date** | [YYYY-MM-DD] |

---

## 1. Networking & Topology
*Define the network layout, security boundaries, and traffic flow.*

*   **Infrastructure Topology Diagram:**
    *   *Keywords:* `VPC`, `Public Subnet`, `Private Subnet`, `NAT Gateway`, `Internet Gateway`, `Mermaid Diagram`.
    *   *Instruction:* Modify the Mermaid chart below to represent your network layout.
    ```mermaid
    graph TD
        Internet((Internet)) --> WAF[Cloud WAF]
        WAF --> ALB[Application Load Balancer]
        subgraph VPC [VPC: 10.0.0.0/16]
            subgraph PublicSubnets [Public Subnets - 10.0.1.0/24]
                ALB
                NAT[NAT Gateway]
            end
            subgraph PrivateSubnets [Private Subnets - 10.0.10.0/24]
                App[App Instance / EKS Worker Nodes]
            end
            subgraph IsolatedSubnets [Isolated Subnets - 10.0.20.0/24]
                DB[(Managed DB: RDS)]
            end
        end
        ALB --> App
        App --> DB
        App --> NAT
        NAT --> Internet
    ```
*   **Subnet Allocation & Security Zones:**
    *   **Public Subnet:** Hosts public load balancers (ALB), NAT Gateways, Bastion Hosts. Accessible from the internet.
    *   **Private Subnet:** Hosts App nodes and private services. No direct inbound internet access; outbound access via NAT Gateway.
    *   **Isolated Subnet:** Hosts database clusters and caches. No internet access (inbound/outbound); only internal connections from the Private Subnet.

## 2. Cloud Resources & Compute
*Define the specific managed cloud services selected for compute, storage, and identity management.*

*   **Compute Services:**
    *   *Keywords:* `Kubernetes (EKS/AKS/GKE)`, `VM Instance (EC2)`, `Serverless (ECS Fargate/Lambda)`.
    *   *Description:* Specify compute selection and instance sizes (e.g., using AWS EKS for containerized microservices).
*   **Storage & Database Services:**
    *   *Keywords:* `Managed DB (RDS PostgreSQL)`, `NoSQL (DynamoDB)`, `Object Storage (S3)`.
    *   *Description:* Define persistence types, replication, and encryption settings.
*   **Identity & Access Management (IAM):**
    *   *Keywords:* `IAM Roles`, `Least Privilege Principle`, `KMS (Key Management Service)`.
    *   *Description:* Restrict permissions for cloud services and manage encryption keys (e.g., using KMS for S3 bucket encryption).

## 3. Infrastructure as Code (IaC) & CI/CD
*Define the delivery pipeline and resource provisioning strategy.*

*   **Infrastructure as Code (IaC):**
    *   *Keywords:* `Terraform`, `Ansible`, `CloudFormation`.
    *   *Description:* Standardize infrastructure setup via declarative code modules.
*   **CI/CD Pipeline Workflow:**
    *   *Keywords:* `GitHub Actions`, `GitLab CI`, `ArgoCD (GitOps)`, `Container Registry (ECR/GCR)`.
    *   *Description:* Define steps for building docker images, running pipeline checks, pushing to registries, and deployment.

## 4. High Availability & Disaster Recovery (HA & DR)
*Detail system resiliency and data backup policies.*

*   **High Availability (HA):**
    *   *Keywords:* `Multi-AZ deployment`, `Auto Scaling Group (ASG)`, `Target Groups`.
*   **Disaster Recovery (DR) Targets:**
    *   *Keywords:* `RTO (Recovery Time Objective)`, `RPO (Recovery Point Objective)`.

| Metric | Target | Disaster Recovery Strategy |
| :--- | :--- | :--- |
| **RTO (Max Downtime)** | e.g., < 4 Hours | Multi-region secondary cluster, automated IaC environment spin-up |
| **RPO (Max Data Loss)** | e.g., < 1 Hour | Relational DB snapshots every hour, transactional replication |

## 5. Observability & Operations
*Design system health tracking, tracing, and alert delivery.*

*   **Metrics & Dashboards:**
    *   *Keywords:* `Prometheus`, `Grafana`, `AWS CloudWatch`, `Datadog`.
    *   *Description:* Collect CPU, Memory, Disk usage, and API response counts.
*   **Centralized Logging:**
    *   *Keywords:* `ELK Stack (Elasticsearch, Logstash, Kibana)`, `Loki`, `FluentBit`.
*   **Alerting & On-Call Escalation:**
    *   *Keywords:* `Slack notifications`, `PagerDuty`, `Opsgenie`.
    *   *Description:* Trigger alerting rules (e.g., alert on-call team if HTTP 5xx error rate > 2% or CPU > 85% for 5 mins).
"""
    HLD_TECH = """
# HIGH-LEVEL TECHNICAL DESIGN (HLD - TECHNICAL)

| Project / System Name | [Project/System Name] |
| :--- | :--- |
| **Status** | Draft / Under Review / Approved |
| **Author** | [Lead Engineer / Tech Lead] |
| **Version** | v1.0.0 |
| **Date** | [YYYY-MM-DD] |
| **Approver(s)**| [Approver Name] |

---

## 1. Technology Stack
*Define the languages, frameworks, runtime environments, databases, and core libraries used.*

*   **Tech Stack Matrix:**
    *   *Keywords:* `Framework`, `Runtime`, `Database Engine`, `Message Broker`.

| Layer / Component | Technology Selected | Version | Justification / Reason |
| :--- | :--- | :--- | :--- |
| **Backend API** | e.g., Node.js (NestJS) / Java (Spring Boot) | e.g., v20 LTS / v17 | Familiarity of the team, ecosystem, and performance |
| **Frontend Web** | e.g., React / Next.js | e.g., v14 | Server-side rendering support, SEO friendliness |
| **Database** | e.g., PostgreSQL | e.g., v15 | Relational integrity (ACID compliance) |
| **Caching** | e.g., Redis | e.g., v7.0 | High-performance in-memory key-value store |

## 2. Database Design & Caching
*Describe the database schema design, access patterns, and cache layers.*

*   **Entity Relationship Diagram (ERD):**
    *   *Keywords:* `PK`, `FK`, `One-to-Many`, `Mermaid ERD`.
    *   *Instruction:* Customize the Mermaid ERD below to model your relational schema.
    ```mermaid
    erDiagram
        USERS ||--o{ ORDERS : places
        USERS {
            int id PK
            string username
            string email
            string password_hash
        }
        ORDERS {
            int id PK
            int user_id FK
            string order_status
            decimal total_amount
            timestamp created_at
        }
    ```
*   **Indexing & Partitioning Strategy:**
    *   *Keywords:* `Composite Index`, `B-Tree Index`, `Table Partitioning`, `Execution Plan`.
    *   *Description:* Specify fields that require indexing (e.g., query constraints in `WHERE` or fields in `JOIN`/`ORDER BY` clauses).
*   **Caching Strategy:**
    *   *Keywords:* `Cache-Aside Pattern`, `Write-Through`, `TTL (Time-To-Live)`, `Cache Eviction`.
    *   *Description:* Define the caching mechanism, caching duration (TTL), and cache invalidation policies.

## 3. API Specifications
*Define communication standards, response schemas, and authentication models.*

*   **API Design Standards:**
    *   *Keywords:* `RESTful API`, `GraphQL`, `gRPC`, `Naming Convention (camelCase / snake_case)`.
*   **Standard JSON Response Structure:**
    ```json
    {
      "success": true,
      "data": {
        "id": 123,
        "name": "Sample Product"
      },
      "error": null
    }
    ```
*   **Authentication & Authorization:**
    *   *Keywords:* `JWT`, `OAuth 2.0`, `Bearer Token`, `RBAC (Role-Based Access Control)`.
    *   *Description:* Describe the authorization model (e.g., passing JWT in the HTTP header: `Authorization: Bearer <token>`).

## 4. Error Handling & Logging
*Detail how errors are caught, handled, and logged across the application layers.*

*   **Error Handling Strategy:**
    *   *Keywords:* `Global Exception Filter`, `Try-Catch block`, `HTTP Status Codes`.
    *   *Description:* Define standard error response structure and HTTP status mapping (e.g., 400 for Bad Request, 500 for Internal Server Error).
*   **Logging Standards:**
    *   *Keywords:* `Winston/Logback`, `Log level (DEBUG, INFO, WARN, ERROR)`, `Correlation ID`, `Log Masking`.
    *   *Description:* Ensure that all logs are structured (JSON format) and include a `Correlation ID` for tracing asynchronous flows.

## 5. Code Quality & Testing Strategy
*Define testing methodologies, code styles, and pipeline integration thresholds.*

*   **Software Testing Strategy:**
    *   *Keywords:* `Unit Test`, `Integration Test`, `Coverage Target (e.g., >= 80%)`.
    *   *Description:* Specify test runners (e.g., Jest, JUnit, PyTest) and mocking policies.
*   **Coding Standards & Static Analysis:**
    *   *Keywords:* `ESLint`, `Prettier`, `SonarQube Scan`, `Static Code Analysis`.

## 6. Application Security
*Document security practices implemented within the application codebase.*

*   **Encryption:**
    *   *Keywords:* `bcrypt` (password hashing), `AES-256` (data-at-rest), `TLS 1.3` (data-in-transit).
*   **OWASP Top 10 Mitigation:**
    *   *Keywords:* `SQL Injection Protection (Parameterized queries)`, `XSS Protection (Sanitization)`, `Rate Limiting`.
"""
    LLD_ARCH = """
# LLD-Architecture Design Template

## 1. Introduction and Scope

- Objective: Explain that this document describes the detailed software architecture for the system or module (e.g., _“E-commerce System – Order Service Architecture”_).
- Scope: State which components and interactions are covered. Reference related HLD diagrams or requirements.
- Audience: (e.g., system architects, developers, DevOps).

## 2. System Context

- Context Diagram: Present a high-level diagram (often from HLD) showing the system’s boundaries and its external entities (users, external systems, services). Indicate data flows.
- Components: List major system components/services (e.g., _Web Frontend, API Gateway, Order Service, Payment Gateway_) and their brief roles.
- Communication Protocols: Note protocols used between components (REST, messaging queues, RPC).
- Design Style: State architectural style (e.g., microservices, layered, event-driven) and reasoning.
- _Usage:_ This aligns with the SDD “context” and “composition” viewpoints to map external interactions into system structure.

## 3. Logical Component Design

- Diagrams: Include UML component or class diagrams illustrating the internal structure of each major module. Show key classes, interfaces, and relationships (inheritance, aggregation).
- Component Descriptions: For each major component/service:
  - _Responsibilities:_ What it does (e.g., _“InventoryService: Manages stock levels and quantities”_).
  - _Public Interfaces:_ APIs or interfaces it exposes.
  - _Key Classes:_ List core classes/objects with their roles.
- Relationships: Show how components depend on or use each other (e.g., _“OrderService calls InventoryService.checkStock()”_).
- Sequence Flows: For critical processes (e.g., order creation), provide a sequence diagram indicating method calls across components.

## 4. Interaction Diagrams

- Sequence Diagrams: Present flow of events for important scenarios (e.g., _User places an order: UI → OrderAPI → Inventory → Payment → Notification_).
- Protocol Details: Specify message formats or events (e.g., JMS messages, HTTP payloads).
- Integration Points: Document how external systems integrate (third-party payment API, email service).

## 5. Technology Stack and Infrastructure

- Languages/Frameworks: List programming languages, frameworks, and major libraries used by each component (e.g., Spring Boot for services, React for UI).
- Database and Storage: Reference database technologies per component (e.g., PostgreSQL for orders, Redis for caching).
- Infrastructure: Describe deployment environment (containers, cloud platform, on-prem). Include a deployment/network diagram: servers, load balancers, etc.
- DevOps: Note CI/CD tools, configuration management, and environments (dev, test, staging, prod).

## 6. Design Patterns and Decisions

- Patterns: Identify key design patterns applied in the architecture (Singleton, Factory, Observer, etc.), with rationale. Example: _“Singleton – DatabaseConfig to ensure a single DB connection pool”_.
- Trade-offs: Document significant design choices (synchronous vs asynchronous, monolith vs microservices) and reasons.
- Performance: Outline caching strategies (in-memory caches, HTTP caching) and load balancing setup.

## 7. Non-Functional (NFR) Considerations

- Scalability: Explain how the architecture scales (horizontal scaling, stateless services).
- Availability/Reliability: Describe fault tolerance (redundancy, failover, health checks).
- Security Architecture: Detail authentication/authorization flow (e.g., OAuth gateway), encryption in transit and at rest, and how threats are mitigated (input validation, firewalls).
- Monitoring & Logging: Specify logging framework and monitoring tools (metrics, alerts).
- Concurrency: Note how concurrency is handled (thread pools, async processing) as relevant.

## 8. Deployment & Environments

- Environments: Describe different deployment environments (Dev, QA, Prod) and their configurations.
- Deployment Diagram: (Optional) Show physical deployment view (servers, containers, databases in each environment).
- Config Management: Note where configuration (e.g., app settings, secrets) is stored and how it’s managed across environments.

## 9. Appendices

- Glossary: Define any architectural terms or acronyms.
- Reference Documents: List related documents (HLD, SRS).
- Change Log: Track architectural changes or version updates.

> _Guidance:_ The architecture section should map out components and flows in detail. Include class/component diagrams to define structure and illustrate how data flows through the system. Clearly explain each component’s role and interactions so developers understand where each module fits in the overall architecture.

Sources: Industry best practices and standards (SDD/IEEE 1016) recommend covering data structures, interfaces, architecture, and procedures in detail. Use these guidelines to ensure your templates are complete and actionable.
"""
    LLD_DB = """
# LLD-DB Design Template

## 1. Purpose and Scope

- Objective: Briefly state that this document provides the detailed database design for the specified module or feature. Explain which part of the system it covers (e.g., “User Management Database Schema”).
- Scope: Define what’s in and out of scope (e.g., specific features, tables, or modules). Link to higher-level requirements or use cases.
- Audience: List intended readers (e.g., database engineers, developers).

## 2. Database Overview

- Database Type: Specify the kind of database (e.g., _Relational SQL_, _NoSQL_, _Graph_, etc.) and rationale for choosing it.
- Data Domains: Summarize the main data entities or bounded contexts (e.g., _users_, _orders_, _inventory_) and how they relate to system functionality.
- Design Principles: State normalization level (3NF, denormalization, etc.) and any conventions used. Cite IEEE SDD _“data-driven design”_ guidance – this section describes structures and relationships of data objects.
- High-Level Data Model: Provide a brief description of how data will be organized (e.g., one database per service, shared schema, caching layers).

## 3. Entity-Relationship Diagram (ERD)

- Diagram: Include (or link to) an ERD showing all tables (entities), their attributes, primary/foreign keys, and relationships (one-to-one, one-to-many, many-to-many). Use standard notation.
- Key Entities: For each entity, give a short description (e.g., _“User – stores login and profile data.”_).
- Cardinality and Constraints: Note cardinalities and any important constraints (e.g., cascade deletes, uniqueness).

## 4. Table Schemas

- Schema Definition: For each table, list: table name, column names, data types, primary key, foreign keys, default values, and constraints (NOT NULL, UNIQUE, CHECK). Provide a brief description of each column’s purpose.
- Normalization: Explain how tables conform to normalization rules (or justify any intentional denormalization).
- Relationships: Describe how foreign keys link tables (e.g., _Order (order_id, user_id…): user_id is a FK referencing User.user_id_).
- Reference: Follow best practices by designing normalized schemas and documenting each table in detail.

## 5. Indexes and Performance Optimization

- Indexes: List indexes created on tables (single-column or composite), and justify each (e.g., which queries it accelerates). Indicate unique vs. non-unique indexes.
- Partitioning/Sharding: If used, describe partition keys or sharding strategy.
- Query Plan / Tuning: For critical queries (e.g., large joins or reports), outline expected execution plans or optimizations (e.g., covering indexes).
- Performance Goals: State any performance requirements (e.g., query < 100ms for 1M records).
- Reference: Include index design rationale and any performance benchmarking, as suggested for low-level design.

## 6. Stored Procedures, Triggers, and Views

- Stored Procedures/Functions: List any database procedures or functions, with their purpose and key logic. (E.g., _ValidateUserCredentials: checks password and updates last_login._)
- Triggers: Document database triggers (e.g., _AFTER INSERT on Orders updates Inventory_), including conditions and actions.
- Views: Describe any database views used for reporting or abstraction.
- Logic Notes: Provide brief pseudocode or SQL comments for complex logic if needed.

## 7. Sample Queries and Data Access Patterns

- Critical Queries: Provide example SQL queries or statements for major operations (e.g., retrieving user order history, updating status). Annotate them to highlight joins, filters, and logic.
- Data Access: Note how application code accesses the DB (e.g., through ORM, raw SQL). If using an ORM, explain table-to-object mappings.
- Security: Mention any query-level security (row-level filters, etc.).

## 8. Data Migration and ETL (if applicable)

- Migration Strategy: If migrating existing data, outline the ETL approach or scripts. Include sample transformation rules (e.g., migrating legacy user IDs).
- Seed Data: List initial or lookup tables data that must be populated (e.g., _UserRoles, Countries_).
- Constraints/Triggers: Ensure referential actions or data integrity checks for migration.

## 9. Security and Compliance

- Sensitive Data: Identify columns with sensitive information (e.g., PII) and how they are protected (e.g., encryption at rest, masking).
- Access Control: Specify how database permissions are granted (e.g., GRANT statements or roles). Define who can read/write specific tables.
- Auditing: If applicable, note any audit logs or change tracking.
- Regulatory: Address compliance (e.g., GDPR retention policies, encryption standards).

## 10. Backup and Recovery

- Backup Strategy: Describe backup frequency (full vs incremental), retention policy, and storage location.
- High Availability: Outline replication or clustering (e.g., master-slave, multi-AZ).
- Recovery Plan: Summarize steps to restore from backup (point-in-time recovery).

## 11. Appendices

- Data Dictionary: (Optional) A glossary of database terms, abbreviations, and domain-specific names.
- DDL Scripts: Reference or attach actual DDL SQL scripts for tables, indexes, etc.
- Revision History: Track document changes (version, date, author, summary).

> _Guidance:_ Ensure the LLD-DB document is a reference for developers/DBAs, with clear tables, diagrams, and explanation of data organization. It should enable building and querying the database without ambiguity.
"""
    LLD_API = """
# LLD-API Design Template

## 1. Purpose and Scope

- Objective: State that this document details the API design for specific services or modules (e.g., _“Authentication and User Service API”_).
- Scope: Clarify which endpoints are covered and their relation to user stories or features. Reference related HLD or interface docs.
- Audience: (e.g., API developers, integrators, QA).

## 2. API Overview and Standards

- API Style: Specify type (RESTful, GraphQL, gRPC, etc.) and justify choice.
- Specification Format: State that the API is defined using an OpenAPI/Swagger specification (version), allowing automation of docs.
- Naming Conventions: Summarize URL and method naming rules (e.g., nouns for resources, use of plurals).
- Versioning Scheme: Describe URI versioning or headers (e.g., _/v1/users_).
- Base URL and Protocols: Provide the base path and protocols (HTTPS).

## 3. Authentication & Authorization

- Auth Method: Describe authentication mechanism (e.g., OAuth2 Bearer tokens, JWT, API keys).
- OAuth Flows/Roles: If OAuth2, specify grant types; list user roles or scopes required for each endpoint.
- Headers: List required auth headers (e.g., `Authorization: Bearer <token>`).
- Access Rules: For each endpoint (or group), note any special permissions or roles needed.

## 4. Endpoints and Methods

- Endpoint Catalog: Provide a table or list of all endpoints with: HTTP method, URL path, brief description, and related functionality. Group endpoints by resource (e.g., _Users_, _Orders_).
- Path Parameters: For each endpoint, detail path and query parameters (name, type, description, required/optional).
- Examples: Include example requests for clarity (e.g., `curl` examples or code snippets).

## 5. Request and Response Specifications

- Request Payloads: For POST/PUT endpoints, define the JSON (or XML) schema of the request body. List all fields with types, required status, and validation rules. Example:

  ```json
  {
    "username": "string (required, max 50 chars)",
    "password": "string (required)",
    "email": "string (required, format: email)"
  }
  ```

- Response Schemas: Define the success response format (200/201) as a JSON schema or example. List fields and meanings. Provide examples of both success and error responses.
- Status Codes: Enumerate HTTP status codes used (200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Server Error, etc.) and conditions for each.
- Error Format: Specify standard error response structure (e.g., `{"error": "InvalidInput", "message": "Username is required"}`) and provide examples.
- Authentication Details: Reiterate any required tokens/credentials per call if not global.
- Reference: Treat each endpoint’s request/response like a contract as in an API reference – list all fields and auth details.

## 6. Error Handling

- Error Codes and Messages: Define application-specific error codes or codespace. Map to HTTP status codes.
- Validation Errors: Document how input validation failures are returned (e.g., which fields are invalid).
- Common Errors: List shared error cases (401 Unauthorized, 429 Too Many Requests) and their JSON structure.
- Error Logging: (Optional) Mention correlation IDs or headers used for tracing requests.

## 7. Rate Limiting and Throttling

- Limits: If applicable, state any API rate limits (requests per minute/hour per user or API key).
- Throttling Behavior: Describe what happens when a client exceeds the limit (response code 429, retry-after header).
- Versioning and Deprecation: If supporting multiple API versions, explain deprecation policy for old endpoints.

## 8. Security and Compliance

- Transport Security: Enforce HTTPS/TLS. Mention any required cipher standards or certificate pinning.
- CORS Policy: If relevant (for browser clients), state cross-origin access rules.
- Data Protection: Ensure sensitive data in requests/responses is handled securely (e.g., never return passwords).
- Compliance: Address any legal requirements (e.g., logging sensitive fields, GDPR requirements).

## 9. Usage Examples

- Code Samples: Provide example code snippets in relevant languages (cURL, Java, Python) for common tasks (authentication, CRUD operations).
- Use Cases: Illustrate typical usage flows (e.g., _User signs up → API call → confirmation response_).
- SDKs/Clients: (Optional) Mention any auto-generated SDKs or client libraries.

## 10. Appendices

- OpenAPI/Swagger File: Reference the canonical API spec file (JSON/YAML) and instructions on accessing it.
- Change Log: Track endpoint changes over versions (new endpoints, parameter changes).
- Glossary: Define any specialized terms (e.g., “tenant”, “scope”).

> _Guidance:_ Follow API reference best practices – list every endpoint, with its request parameters, payload, and response format. Use machine-readable specs (OpenAPI) to ensure accuracy.
"""
    LLD_PSEUDO = """
# LLD-Pseudocode Design Template

## 1. Purpose and Scope

- Objective: State that this document provides the detailed logic and algorithmic design for specified features or modules (e.g., _“Order Processing Logic”_).
- Scope: Clarify which business logic or modules are covered (e.g., validation rules, core algorithms). Link to user stories or requirements.
- Audience: (e.g., developers implementing code, QA reviewing logic).

## 2. Functional Decomposition

- Modules/Functions List: Enumerate the main functions or processes. For each, give a brief description. Example:
  - _`ValidateOrder(order)` – Checks stock and payment details._
  - _`CalculateShipping(order)` – Computes shipping cost based on weight and region._
- Dependencies: Note dependencies between these functions (e.g., _“CalculateShipping is called after order validation”_).
- Inputs/Outputs: For each function, list expected inputs and outputs (data structures or parameters).

## 3. Pseudocode for Each Algorithm

- Structured Pseudocode: For each module/function above, provide pseudocode that outlines the step-by-step logic. Use a consistent style (e.g., `BEGIN`/`END`, indentation, keywords like IF, FOR). Example:

  ```
  FUNCTION AddRole(roleName, memberId)
      IF RoleExists(roleName) THEN
          RETURN "Error: No duplication of roles allowed"
      ELSE
          INSERT INTO Roles (name) VALUES (roleName)
          ASSIGN role to Member(memberId)
          RETURN "Role added successfully"
      ENDIF
  END FUNCTION
  ```

- Clarity: Use clear, descriptive names (avoid vague placeholders). Focus on logic flow, not syntax of a specific language. Mention condition branches and loops explicitly.
- Comments: Optionally include brief comments for complex steps.
- Standards: Follow general pseudocode best practices (keywords uppercase, no language-specific syntax).

## 4. Data Structures

- Structures Used: For each algorithm, identify data structures (arrays, lists, trees, hash maps, queues, etc.) and explain their role. Example: _“Use a hash map for `userSessions` to allow O(1) lookup by session ID.”_
- Design Rationale: Explain why a structure was chosen (e.g., efficient search, maintain order).
- Size Estimates: Note expected sizes or limits (e.g., maximum list length) if known.

## 5. Time and Space Complexity

- Complexity Analysis: For each algorithm or critical section, state the time complexity (Big-O) and space complexity. Example: _“`sortItems()`: O(n log n) time using merge sort, O(n) auxiliary space.”_
- Justification: Briefly justify complexity (e.g., choice of algorithm or data structure).
- Performance Requirements: If there are performance constraints (e.g., must handle 10,000 items), note them here.
- Reference: Include algorithm complexity analysis as part of detailed design.

## 6. Edge Cases and Error Handling

- Edge Conditions: List special cases that need handling (empty input, null values, maximum/minimum limits). Example: _“If input list is empty, return null or default value.”_
- Error Handling: Specify how errors are dealt with (exceptions, return codes). Example: _“If authentication fails, return an `InvalidCredentials` error.”_
- Validation: Describe input validation logic not covered elsewhere (e.g., format checks).
- Fallbacks: Mention any fallback or retry logic (e.g., what happens on external service failure).
- Reference: Cover edge-case robustness as emphasized in design guidelines.

## 7. Sample Flowcharts or Diagrams (Optional)

- Visual Flow: If helpful, include a flowchart or sequence diagram for complex logic flows.
- Steps Illustration: Annotate steps to correspond with pseudocode blocks (start, decisions, loops, end).
- Clarity Aid: These visuals should clarify the algorithm steps for stakeholders.

## 8. Appendices

- Example Test Cases: (Optional) Provide sample input and output to illustrate function behavior.
- Glossary: Define any specialized algorithmic terms or abbreviations used.

> _Guidance:_ This pseudocode section should make the implementation obvious to a developer. Break down each operation into clear logical steps, and document complexities using Big-O notation. Use pseudocode to capture logic before writing actual code.
"""
    RTM = """
# Requirements Traceability Matrix (RTM) Template
## Document Control

- Version: Document version identifier.
- Date: Last updated date.
- Author: Person who prepared the RTM.
- Reviewed by: Stakeholders who approved the RTM.
- Revision History: Table of revisions.

## Purpose

- Define the objectives of the RTM (e.g., ensuring every requirement is linked to design and test artifacts, supporting traceability and compliance).
- Explain how the RTM will be used (e.g., coverage analysis, impact analysis, audit preparation).

## Scope

- Specify what the RTM covers (project, system, components).
- List requirement types included (e.g., functional, non-functional, business, regulatory).
- Note any exclusions (e.g., out-of-scope modules or phases).

## Definitions / Acronyms

- Define key terms and acronyms (e.g., RTM, requirement ID, test case, sprint, etc.) for clarity.

## Naming Conventions

- Requirement ID: Use a consistent format with clear prefixes (e.g., “FR-001” for functional req, “NFR-002” for non-functional req).
- Test Case ID: Use a corresponding format (e.g., “TC-001” for test cases).
- Document naming rules for other artifacts as needed (e.g., design modules, APIs).
- Ensure the format is documented and communicated to all team members.

## Roles and Responsibilities

- RTM Owner: Individual responsible for maintaining and updating the RTM (often a Business Analyst, QA Lead, or Project Manager).
- Reviewers: Team members responsible for periodic reviews (e.g., Project Manager, QA Lead).
- Data Contributors: People who provide or update requirement details, test results, defect links.
- Stakeholders: Who should be informed of updates or changes.

## Traceability Matrix Structure

The RTM should be organized as a table linking requirements to related artifacts. Include at least the following columns:

- Requirement ID: Unique identifier for each requirement.
- Requirement Description: Brief, clear description of the requirement.
- Category/Type: Requirement category (Functional, Non-Functional, Business, etc.).
- Source/Origin: Origin of the requirement (e.g., stakeholder, document, regulation).
- Priority: Business priority or urgency of the requirement (e.g., High, Medium, Low).
- Owner: Person or team responsible for the requirement.
- Acceptance Criteria: Conditions or measurable results required for the requirement to be considered met.
- Design/Module: (Optional) References to design documents, modules, or components implementing the requirement.
- Dependencies: (Optional) IDs of related requirements that depend on or influence this requirement.
- Test Case ID: Identifier(s) of test case(s) covering this requirement.
- Test Case Description: Short description of each linked test case.
- Test Result/Status: Outcome or status of each test (e.g., Pass, Fail, In Progress).
- Defect/Issue ID: Any defect or issue IDs resulting from tests of this requirement.
- Requirement Status: Current progress state of the requirement (e.g., Draft, In Progress, Completed).
- Comments/Notes: Additional remarks or context about the requirement.
- Potential Risks: (Optional) Known risk factors impacting the requirement.

_(Adjust or extend columns as needed for project specifics.)_

## Matrix Maintenance and Updates

- Living Document: The RTM must be kept up-to-date; update it whenever requirements, tests, or defects change.
- Updates: Record new requirements, changes in status, test results, and defect associations promptly.
- Owner: The RTM Owner (e.g., BA or QA Lead) is responsible for regular maintenance.
- Review Cycle: Conduct reviews at each milestone or sprint, and after any major change, to ensure accuracy.
- Versioning: Apply version numbers to the RTM (e.g., RTM_v1.0, RTM_v1.1) and document all changes.
- Traceability Audit: Periodically verify that all requirements have corresponding test cases and that coverage is complete. Address any gaps.

## Revision History

Maintain a table of all RTM revisions:

- Version | Date | Author | Description of Changes
- Example: v1.0|2026-07-09|Jane Doe|Initial RTM draft.
- Update this table with each new version of the RTM.

## References

- Link to the Master Requirements Document, design specifications, test plan, and other artifacts used to populate the RTM.
- Cite any guidelines or standards referenced (e.g., IEEE/ISO requirements standards).
"""
    STAKEHOLDER_REGISTER = """
| Name | Organization | Role | Phone | Email | Location | Stakeholder Type | Stakeholder Classification | Impact | Influence | Interest | Communication Frequency | Primary Channel | Secondary Channel | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| John Smith | Global Wind Corp | Partner Management | 1234 123 123 | john.smith@gwc.com | California | External | Primary | Medium | High | High | Daily | Face-to-Face | Online Chat | 12/02/2024 - Mentioned concerns about nearby development impacting project. |
| Grace Mann | Local Council | Project Officer | 543 435 345 | g.mann@ttc.gov | California | External | Secondary | Low | Medium | Medium | Monthly | Phone call | Email | |

***

## Reference Dropdown Values

To maintain consistency and data integrity, please use the following predefined options for the respective columns in the register:

### Stakeholder Type
* Internal
* External

### Stakeholder Classification
* Primary
* Secondary

### Impact
* Low
* Medium
* High

### Influence
* Low
* Medium
* High

### Interest
* Low
* Medium
* High

### Communication Frequency
* Daily
* Weekly
* Fortnightly
* Monthly
* Quarterly
* Yearly

### Primary & Secondary Channels
* Letter
* Phone call
* Email
* SMS
* Facebook
* LinkedIn
* Instagram
* X
* Face-to-Face
* Online Chat
* Consultation Platform
* Task Manager
"""
    HIGH_LEVEL_REQUIREMENTS = """
# High-Level Requirements Document


## I. Overview

* **Project Title:** Development of New Customer Relationship Management (CRM) System
* **Prepared By:** [Your Name]
* **Date:** August 29, 2050
* **Company:** [Your Company Name]
* **Company Address:** [Your Company Address]
* **Email:** [Your Company Email]

***

## II. Objectives

* **Objective 1:** To provide a comprehensive solution for managing customer relationships, including tracking interactions, sales, and support requests.
* **Objective 2:** To improve data accuracy and accessibility through a centralized database that integrates seamlessly with existing business systems.
* **Objective 3:** To enhance user experience with an intuitive interface and customizable features that meet diverse organizational needs.

***

## III. Key Features

### A. Customer Management

#### Feature 1:
* **Customer Profiles:** Detailed records of customer information including contact details, interaction history, and preferences.

#### Feature 2:
* **Interaction Tracking:** Automated logging of all customer interactions including emails, calls, and meetings.

### B. Sales Management

#### Feature 1:
* **Lead Tracking:** Tools for tracking and managing sales leads through the sales pipeline.

#### Feature 2:
* **Sales Forecasting:** Analytical tools to predict future sales trends based on historical data and current pipeline status.

### C. Data Management

#### Feature 1:
* **Centralized Database:** A single repository for all customer and sales data, ensuring consistency and reliability.

#### Feature 2:
* **Data Security:** Advanced security protocols to protect sensitive customer and company data.

***

## IV. Technical Requirements

### A. System Architecture

#### Requirement 1:
* **Scalability:** The system should support scaling up to accommodate increased user load and data volume.

#### Requirement 2:
* **Integration:** Must integrate with existing ERP and marketing systems to ensure data consistency.

### B. Performance

#### Requirement 1:
* **Response Time:** The system should have an average response time of less than 2 seconds for all user actions.

#### Requirement 2:
* **Uptime:** The system should achieve 99.9% uptime over the course of a year.

### C. Compliance

#### Requirement 1:
* **Regulatory Compliance:** The system must comply with relevant data protection regulations such as GDPR and CCPA.

#### Requirement 2:
* **Audit Trails:** Maintain detailed audit trails of user actions for compliance and security purposes.

***

## V. Implementation Plan

### A. Project Phases

| Phase | Description | Timeline |
| :--- | :--- | :--- |
| Planning | Requirements gathering and analysis | 1 Month |
| Design | System design and architecture | 2 Months |
| Development | Coding and system build | 4 Months |
| Testing | Quality assurance and testing | 2 Months |
| Deployment | System rollout and user training | 1 Month |

### B. Risk Management

#### Risk 1:
* **Description:** Potential development delays due to technical challenges.
* **Mitigation Strategy:** Regular progress reviews and contingency planning.

#### Risk 2:
* **Description:** User resistance to new system adoption.
* **Mitigation Strategy:** Comprehensive training and support during rollout.

***

## VI. Stakeholders

### Primary Stakeholders:
* **Sales Team:** Users who will interact with the CRM daily.
* **Customer Support:** Staff responsible for customer interactions and support.

### Secondary Stakeholders:
* **IT Department:** Responsible for system maintenance and integration.
* **Management:** Oversight and approval of project milestones and deliverables.
"""
    REQUIREMENTS_MANAGEMENT_PLAN = """
# Organisation [Name]
## Department [Name]

**Requirements Management Plan**

**Date:** <Date>  
**Doc. Version:**  

***

**Template version:** 3.0.1  
This artefact template is aligned with the PM² Guide V3.0  
For the latest version of the templates visit: https://www.pm2alliance.eu/publications  

The PM² Alliance is committed to the improvement of the PM² Methodology and of its supporting artefact. Project management best practices and community contributions & corrections are incorporated in the PM² Alliance’s artefact templates.  
Join the PM² Alliance and visit the PM² Alliance GitHub to provide your feedback & contribution: https://github.com/pm2alliance  

***

### Document Control Information

| Settings | Value |
| :--- | :--- |
| **Document Title:** | Requirements Management Plan |
| **Project Title:** | |
| **Document Author:** | <Document Author> |
| **Project Owner:** | <Project Owner (PO)> |
| **Project Manager:** | <Project Manager (PM)> |
| **Doc. Version:** | |
| **Sensitivity:** | |
| **Date:** | |

***

### Document Approver(s) and Reviewer(s)

> **NOTE:** All Approvers are required. Records of each approver must be maintained. All Reviewers in the list are considered required unless explicitly listed as Optional.

| Name | Role | Action | Date |
| :--- | :--- | :--- | :--- |
| | | <Approve / Review> | |
| | | | |
| | | | |

***

### Document History

The Document Author is authorized to make the following types of changes to the document without requiring that the document be re-approved:
* Editorial, formatting, and spelling
* Clarification

To request a change to this document, contact the Document Author or Owner.  
Changes to this document are summarized in the following table in reverse chronological order (latest version first).

| Revision | Date | Created by | Short Description of Changes |
| :--- | :--- | :--- | :--- |
| | | | |
| | | | |
| | | | |

***

### Configuration Management: Document Location

The latest version of this controlled document is stored in `<location>`.

***

> **Notes for Templates:**  
> * **Text in `<orange>`:** has to be defined.  
> * **Text in `<blue>`/`*<italic>*`:** guidelines and how to use the Template. Should be deleted in the final version.  
> * **Text in `green`:** can be customised. Should be recoloured to black in the final version.  

***

## TABLE OF CONTENTS

1. [Introduction](#1-introduction)
2. [Requirements Management Objectives](#2-requirements-management-objectives)
3. [Requirements Management process](#3-requirements-management-process)
4. [The Requirements lifecycle](#4-the-requirements-lifecycle)
5. [Requirement Management Roles and Responsibilities](#5-requirement-management-roles-and-responsibilities)
6. [Tools and Techniques](#6-tools-and-techniques)
   * 6.1. [Requirements documentation](#61-requirements-documentation)
   * 6.2. [Requirements traceability matrix](#62-requirements-traceability-matrix)
7. [Requirements change management](#7-requirements-change-management)
8. [Related PM² Plans](#8-related-pm-plans)
9. [Appendix 1: References and Related Documents](#appendix-1-references-and-related-documents)

***

## 1. Introduction

* Define Requirements Management process, roles, responsibilities, standards, and tools for the project.

***

## 2. Requirements Management Objectives

* **Goal:** Gather, document, validate, and manage project requirements throughout the project lifecycle.
* **Deliverables:** Requirements Documentation, Requirements Traceability Matrix (RTM).
* **Integration:** Align and manage changes with the Project Change Management Plan.

***

## 3. Requirements Management process

*<Please tailor the requirements management process if necessary>*

* **Step 1: Specify:** Gather requirements from stakeholders and document in Requirements Documentation.
* **Step 2: Evaluate:** Assess feasibility, cost, scope alignment, priority (e.g., MoSCoW), and define acceptance criteria.
* **Step 3: Approve:** Formally agree on requirements and priorities (logged in Decision Log/Minutes).
* **Step 4: Monitor:** Track implementation progress and manage new/changed requirements via change control.
* **Step 5: Validate:** Verify deliverables against acceptance criteria with User Representatives.

***

## 4. The Requirements lifecycle

* **Stages:**
  * **Specified:** Documented.
  * **Proposed:** Evaluated, awaiting client approval.
  * **Approved:** Formally approved.
  * **Incorporated:** Added to Project Work Plan (PWP).
  * **Implemented:** Built and tested by the team.
  * **Validated:** Formally accepted by the client.
* **Special Statuses:**
  * **For Fixing:** Issue identified, requires resolution.
  * **Rejected:** Obsolete, out of scope, or duplicated.

***

## 5. Requirement Management Roles and Responsibilities 

* **Project Owner (PO):** Accountable for all requirements, approves/rejects documentation and priorities.
* **Project Steering Committee (PSC):** Informed on requirements status and change requests.
* **Business Manager (BM):** Identifies User Representatives (UR), assists in prioritizing and testing.
* **Solution Provider (SP):** Informed on requirements status.
* **Project Manager (PM):** Responsible for managing, monitoring, and reporting requirements.
* **Project Core Team (PCT):** Supports implementation and analysis.
* **Appropriate Governance Body (AGB):** Informed on status.
* **Other Stakeholders:** *<Please add other stakeholders if relevant.>*

| RAM (RASCI) | AGB | PSC | PO | BM | UR | SP | PM | PCT |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Requirements Management Plan** | I | I | A | C | C | I | R | S |
| **Manage Requirements** | I | I | A | C | C | I | R | S |

*\*AGB: Appropriate Governance Body.*  
The contact details of each of the above stakeholders are documented in the Project Stakeholder Matrix.

***

## 6. Tools and Techniques

* **Techniques:** Interviews, Brainstorming, Workshops, Observation, Prototyping, MoSCoW prioritization.
* **Tools:** Requirements documentation, Requirements Traceability Matrix (RTM).

***

### 6.1. Requirements documentation

*<Define the documentation structure to be used for requirements management>*

| Attribute | Description / Details |
| :--- | :--- |
| **ID** | Unique requirement identifier (numbered sequentially). |
| **Name** | Short name of the requirement. |
| **Category** | e.g. Business need, Feature, Functional, Technical, Quality, Performance, Security, etc. |
| **Type** | e.g. Epic, User story, Story board, Use Case, UI sketch, Business Process Model, etc. |
| **Requirement Description & Details** | Text description or diagrams/sketches. |
| **Acceptance Criteria** | Criteria used to test if the deliverable meets the requirement. |
| **Status** | e.g. Specified, Proposed, Approved, Incorporated, Implemented, Validated, For Fixing & Rejected. |
| **Requested by** | Stakeholder source of the requirement. |
| **Identification Date** | Date the requirement was raised. |

*The above is a suggested list of attributes. No template is provided.*

***

### 6.2. Requirements traceability matrix

*<Define the Traceability Matrix structure to be used for tracking relations between requirements and deliverables>*

| Attribute | Description / Details |
| :--- | :--- |
| **ID** | Unique identifier. |
| **Name** | Short and descriptive name. |
| **Status** | e.g. Specified, Proposed, Approved, Incorporated, Implemented, Validated, For Fixing & Rejected. |
| **Priority** | e.g. High, Medium, Low or Must-have, Should-have, Could-have, Won't-have. |
| **Size** | Estimated effort level (Big, Medium, Small). |
| **Comments** | Notes or reasons for rejection. |
| **Derived From** | Parent requirement ID (e.g. Business requirement). |
| **Related WBS code** | WBS element code producing the deliverable. |
| **Specification of documentation** | Reference document name and file location. |
| **Test Plan** | Test plan or acceptance criteria document location. |

*The above is a suggested list of attributes. No template is provided.*

***

## 7. Requirements change management

*<Customise the process that will be used to manage change to the requirements for this project.>*

* Log new or changed requirements using the **Change Request Form**.
* Process changes through the Requirements Management process and **Project Change Management Plan**.

***

## 8. Related PM² Plans

* **Project Handbook:** Establishes high-level project goals, standards, and escalation processes.
* **Project Change Management Plan:** Manages scope, budget, and timeline modifications.
* **Deliverable Acceptance Plan:** Outlines validation process and acceptance criteria.

***

## Appendix 1: References and Related Documents

*<Use this section to reference any relevant or additional information.>*

| ID | Reference or Related Document | Source or Link/Location |
| :--- | :--- | :--- |
| **1** | *<Example of a related document>*<br>04.Project_Handbook.XYZ.11-11-2017.V.1.0.docx | *<Example of a location>*<br>`< U:\METHODS\ProjectX\Documents\>` |
| **2** | | |
| | | |
| | | |
| | | |
| | | |


"""
    SCOPE_STATEMENT = """
A project scope statement is a clear definition of the boundaries of a project. It includes all the assumptions, responsibilities, requirements, constraints, milestones, and deliverables needed to ensure the project is a success.

***

| Project | Project Manager | Date |
| :--- | :--- | :--- |
| [Name of project] | [Name of project manager] | [Date completed or revised] |

***

| Purpose |
| :--- |
| [Brief explanation of a need and how the project will fulfill that need.] |

***

| Business Objectives |
| :--- |
| [Define targets you want to achieve with the project, such as launch dates, better customer satisfaction, greater conversion rates, etc.] |

***

| Scope Description |
| :--- |
| **In Scope** |
| [Make a list of functionalities that is within the scope of the project.] |
| **Out of Scope** |
| [Make a list of functionalities that is outside the scope of the project.] |

***

| Project Deliverables |
| :--- |
| [Make a list of deliverables that will be produced during the project to meet your business objective.] |

***

| Constraints |
| :--- |
| [List all potential project constraints, such as time, cost, scope, risk, resources, etc.] |

***

| Assumptions |
| :--- |
| [List project assumptions, like the above constraints, to help stakeholders know what resources are going to be required to fulfill the project.] |

***

| | | **Cost Estimate** | | |
| :--- | :--- | :--- | :--- | :--- |
| **Item** | **Estimated Cost** | **Actual Cost** | **Cost Until Completion** | **Variance** |
| [Name of resource] | [Dollar figure for line item cost] | [Actual cost of line item] | [Estimated cost of line item for remaining project] | [Discrepancy between estimated and actual} |
| | | | | |
"""
    PRODUCT_ROADMAP = ""
    FEASIBILITY_STUDY = """
# Feasibility Study

### &lt;Project Name&gt;

**Company Name**  
**Street Address**  
**City, State Zip Code**  

**Date:** [Date]  

***

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Description of Products and Services](#2-description-of-products-and-services)
3. [Technology Considerations](#3-technology-considerations)
4. [Product/Service Marketplace](#4-productservice-marketplace)
5. [Marketing Strategy](#5-marketing-strategy)
6. [Organization and Staffing](#6-organization-and-staffing)
7. [Schedule](#7-schedule)
8. [Financial Projections](#8-financial-projections)
9. [Findings and Recommendations](#9-findings-and-recommendations)

***

## 1. Executive Summary

* Overview of the feasibility study, summarizing key findings, proposed solutions, and overall viability.

***

## 2. Description of Products and Services

* Detailed descriptions of the proposed products or services, highlighting primary features and customer/organizational benefits.

***

## 3. Technology Considerations

* Technical requirements, hosting environment, system integration, security standards, and IT expertise needed.

***

## 4. Product/Service Marketplace

* Analysis of target market, competitors, distribution channels, and customer value proposition.

***

## 5. Marketing Strategy

* Product differentiation, target audience segmentation, promotional channels (e-mail, campaigns), and customer acquisition plans.

***

## 6. Organization and Staffing

* Organizational impact, restructure needs, additional staffing positions, and reporting lines.

***

## 7. Schedule

* High-level timeline, phase constraints, and key milestones (kickoff, design, testing, go-live).

***

## 8. Financial Projections

* Cost-benefit analysis, startup/recurring budget, net present value (NPV), and financial assumptions.

***

## 9. Findings and Recommendations

* Summary of study findings (technology, marketing, organization, financials) and the final recommendation for project selection.
"""
    COST_BENEFIT_ANALYSIS = ""
    RISK_REGISTER = ""
    COMPLIANCE = ""
