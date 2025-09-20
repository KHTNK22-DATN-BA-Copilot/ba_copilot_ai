# SRS Generator Service Flow Diagram

## Overview

The SRS Generator service automates the creation of Software Requirements Specification documents based on user prompts and uploaded Markdown documents.

## Primary Flow Diagram

```mermaid
flowchart TD
    A[User Input: Prompt + MD Files] --> B{Input Validation}
    B -->|Valid| C[Extract Content from MD Files]
    B -->|Invalid| D[Request Additional Information]
    D --> E[User Provides More Info]
    E --> B

    C --> F[Content Preprocessing]
    F --> G[Generate Context Prompt]
    G --> H[Send to LLM Service]

    H --> I[LLM Processing]
    I --> J[Receive LLM Response]

    J --> K[Post-process Response]
    K --> L[Apply SRS Template]
    L --> M[Format as Markdown]

    M --> N[Store Generated Document]
    N --> O[Return Document ID & Content]
    O --> P[Display SRS to User]

    P --> Q{User Action}
    Q -->|Edit| R[Inline Editing]
    Q -->|Export| S[Export as PDF/MD]
    Q -->|Save| T[Update Stored Document]

    R --> U[Update Document]
    U --> T
```

## Detailed Technical Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as SRS API Gateway
    participant VAL as Input Validator
    participant PROC as Content Processor
    participant LLM as LLM Service
    participant DB as Database
    participant STORE as File Storage

    U->>FE: Upload MD files + Enter prompt
    FE->>API: POST /srs/generate
    API->>VAL: Validate input

    alt Input Invalid
        VAL->>API: Validation errors
        API->>FE: 400 Bad Request
        FE->>U: Show validation errors
        U->>FE: Provide corrections
        FE->>API: POST /srs/generate (retry)
    end

    VAL->>PROC: Process valid input
    PROC->>PROC: Extract MD content
    PROC->>PROC: Generate context prompt
    PROC->>LLM: Send prompt for SRS generation

    LLM->>LLM: Process with AI model
    LLM->>PROC: Return generated SRS content

    PROC->>PROC: Apply SRS template
    PROC->>PROC: Format as markdown
    PROC->>DB: Store document metadata
    PROC->>STORE: Save document content

    PROC->>API: Return document ID + content
    API->>FE: 200 OK with SRS data
    FE->>U: Display generated SRS
```

## Error Handling Flow

```mermaid
flowchart TD
    A[API Request] --> B{Authentication}
    B -->|Failed| C[401 Unauthorized]
    B -->|Success| D{Input Validation}
    D -->|Failed| E[400 Bad Request]
    D -->|Success| F{File Processing}
    F -->|Failed| G[422 Unprocessable Entity]
    F -->|Success| H{LLM Service}
    H -->|Timeout| I[408 Request Timeout]
    H -->|Service Error| J[503 Service Unavailable]
    H -->|Success| K{Document Storage}
    K -->|Failed| L[500 Internal Server Error]
    K -->|Success| M[200 OK]
```

## Data Flow Architecture

```mermaid
graph LR
    A[User Input] --> B[Input Layer]
    B --> C[Validation Layer]
    C --> D[Processing Layer]
    D --> E[AI/LLM Layer]
    E --> F[Template Engine]
    F --> G[Storage Layer]
    G --> H[Response Layer]
    H --> I[User Interface]

    subgraph "External Services"
        E1[OpenAI API]
        E2[Claude API]
        E3[Custom LLM]
    end

    E --> E1
    E --> E2
    E --> E3
```
