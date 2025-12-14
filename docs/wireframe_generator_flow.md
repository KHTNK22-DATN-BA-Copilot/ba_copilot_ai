# Wireframe Generator Service Flow Diagram

## Overview

The Wireframe Generator service automatically creates wireframe prototypes from textual requirements and user descriptions.

## Primary Flow Diagram

```mermaid
flowchart TD
    A[User Input: Page Description + Template] --> B{Input Validation}
    B -->|Valid| C[Parse Requirements]
    B -->|Invalid| D[Request Clarification]
    D --> E[User Provides Details]
    E --> B

    C --> F[Extract UI Components]
    F --> G[Identify Layout Structure]
    G --> H[Generate Component Schema]

    H --> I[Send to LLM Service]
    I --> J[LLM Generates JSON Structure]
    J --> K[Validate Generated Schema]

    K -->|Invalid| L[Schema Correction Loop]
    L --> I
    K -->|Valid| M[Apply Wireframe Template]

    M --> N[Generate HTML/CSS]
    N --> O[Create Interactive Elements]
    O --> P[Store Wireframe Data]

    P --> Q[Generate Preview URL]
    Q --> R[Return Wireframe ID + URL]
    R --> S[Display Wireframe to User]

    S --> T{User Action}
    T -->|Edit| U[Inline Editor]
    T -->|Export| V[Export to Figma/HTML]
    T -->|Regenerate| W[Modify Parameters]

    U --> X[Update Wireframe]
    W --> C
```

## Technical Architecture Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as Wireframe API
    participant NLP as NLP Processor
    participant LLM as LLM Service
    participant TPL as Template Engine
    participant GEN as HTML Generator
    participant STORE as File Storage
    participant CDN as CDN/Preview

    U->>FE: Enter description + select template
    FE->>API: POST /wireframe/generate
    API->>NLP: Process natural language input

    NLP->>NLP: Extract UI components
    NLP->>NLP: Identify layout patterns
    NLP->>LLM: Generate component structure

    LLM->>LLM: Create JSON wireframe schema
    LLM->>API: Return structured data

    API->>TPL: Apply selected template
    TPL->>GEN: Generate HTML/CSS code
    GEN->>STORE: Save wireframe files
    STORE->>CDN: Deploy to preview URL

    CDN->>API: Return preview URL
    API->>FE: 200 OK with wireframe data
    FE->>U: Display wireframe preview
```

## Component Recognition Flow

```mermaid
flowchart TD
    A[Text Analysis] --> B{Component Detection}
    B --> C[Form Elements]
    B --> D[Navigation Items]
    B --> E[Content Sections]
    B --> F[Interactive Elements]

    C --> G[Input Fields]
    C --> H[Buttons]
    C --> I[Dropdowns]

    D --> J[Menu Items]
    D --> K[Breadcrumbs]
    D --> L[Sidebar Navigation]

    E --> M[Headers]
    E --> N[Content Blocks]
    E --> O[Cards/Panels]

    F --> P[Modals]
    F --> Q[Tabs]
    F --> R[Accordions]

    G --> S[Wireframe Schema]
    H --> S
    I --> S
    J --> S
    K --> S
    L --> S
    M --> S
    N --> S
    O --> S
    P --> S
    Q --> S
    R --> S
```

## Template Processing Flow

```mermaid
graph TD
    A[Component Schema] --> B{Template Type}
    B -->|Dashboard| C[Dashboard Template]
    B -->|Form| D[Form Template]
    B -->|Landing| E[Landing Page Template]
    B -->|Admin| F[Admin Panel Template]

    C --> G[Apply Dashboard Layout]
    D --> H[Apply Form Structure]
    E --> I[Apply Landing Design]
    F --> J[Apply Admin Structure]

    G --> K[Generate Responsive CSS]
    H --> K
    I --> K
    J --> K

    K --> L[Create Interactive HTML]
    L --> M[Add Basic JavaScript]
    M --> N[Generate Preview]
```

## Error Handling and Retry Logic

```mermaid
flowchart TD
    A[API Request] --> B{Authentication Check}
    B -->|Fail| C[401 Unauthorized]
    B -->|Pass| D{Input Validation}
    D -->|Fail| E[400 Bad Request]
    D -->|Pass| F{NLP Processing}
    F -->|Fail| G[422 Cannot Parse Requirements]
    F -->|Pass| H{LLM Generation}
    H -->|Timeout| I[408 Request Timeout]
    H -->|Fail| J[503 LLM Service Unavailable]
    H -->|Pass| K{Template Application}
    K -->|Fail| L[500 Template Error]
    K -->|Pass| M{File Generation}
    M -->|Fail| N[500 Generation Failed]
    M -->|Pass| O[200 Success]

    I --> P[Retry Logic]
    J --> P
    P --> Q{Retry Count < 3}
    Q -->|Yes| H
    Q -->|No| R[503 Service Unavailable]
```
