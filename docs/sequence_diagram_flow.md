# Sequence Diagram Generation Workflow

## Overview

The Sequence Diagram Generator creates UML sequence diagrams from natural language descriptions or extracted requirements. This service focuses on modeling interactions between different actors, systems, or components over time.

## Core Workflow

```mermaid
flowchart TD
    A[Sequence Diagram Request] --> B[Input Validation]
    B --> C[Extract Requirements]
    C --> D[Identify Actors]
    D --> E[Identify Interactions]
    E --> F[Build Interaction Timeline]

    F --> G[LLM Processing]
    G --> H[Generate Mermaid Code]
    H --> I[Validate Sequence Syntax]

    I --> J{Valid Syntax?}
    J -->|No| K[Error Analysis]
    K --> L[Regenerate with Corrections]
    L --> H

    J -->|Yes| M[Render Preview]
    M --> N[Store Diagram]
    N --> O[Return Response]

    style G fill:#fff3e0
    style H fill:#e8f5e8
    style M fill:#e1f5fe
```

## Detailed Processing Flow

```mermaid
sequenceDiagram
    participant User as User
    participant API as Diagram API
    participant Parser as Requirements Parser
    participant LLM as LLM Service
    participant Validator as Syntax Validator
    participant Renderer as Mermaid Renderer
    participant Storage as Database

    User->>API: POST /diagrams/sequence/generate
    API->>Parser: Extract actors and interactions

    Parser->>Parser: Identify participants
    Parser->>Parser: Map interaction flows
    Parser->>Parser: Determine message types

    Parser->>LLM: Generate sequence diagram
    Note over LLM: Process: actors, interactions, timing

    LLM->>Validator: Validate mermaid syntax
    Validator->>Validator: Check sequence diagram rules

    alt Valid Syntax
        Validator->>Renderer: Generate preview
        Renderer->>Storage: Store diagram
        Storage->>API: Return diagram ID
        API->>User: Return diagram response
    else Invalid Syntax
        Validator->>LLM: Request correction
        LLM->>Validator: Regenerate with fixes
    end
```

## Actor Identification Process

```mermaid
flowchart TD
    A[Input Description] --> B[Text Analysis]
    B --> C[Extract Entities]
    C --> D{Entity Type}

    D -->|Person/Role| E[Human Actor]
    D -->|System/Service| F[System Actor]
    D -->|External API| G[External Actor]
    D -->|Database| H[Data Actor]

    E --> I[Actor Registry]
    F --> I
    G --> I
    H --> I

    I --> J[Deduplicate Actors]
    J --> K[Assign Actor Names]
    K --> L[Define Actor Types]

    style I fill:#e8f5e8
```

## Interaction Mapping

```mermaid
flowchart TD
    A[Identified Actors] --> B[Parse Interactions]
    B --> C{Interaction Type}

    C -->|Request/Response| D[Synchronous Call]
    C -->|Fire and Forget| E[Asynchronous Message]
    C -->|Return Value| F[Response Message]
    C -->|Error Handling| G[Error Flow]

    D --> H[Message Details]
    E --> H
    F --> H
    G --> H

    H --> I[Sequence Order]
    I --> J[Timing Constraints]
    J --> K[Generate Mermaid Syntax]

    style K fill:#e1f5fe
```

## Sample Input/Output

### Input Example

```json
{
  "title": "User Authentication Flow",
  "description": "User logs in, system validates credentials, generates JWT token",
  "actors": ["User", "Frontend", "Backend", "Database"],
  "interactions": [
    {
      "from": "User",
      "to": "Frontend",
      "action": "Enter credentials",
      "type": "sync"
    },
    {
      "from": "Frontend",
      "to": "Backend",
      "action": "POST /auth/login",
      "type": "async"
    }
  ]
}
```

### Generated Mermaid Output

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant D as Database

    U->>F: Enter credentials
    F->>+B: POST /auth/login
    B->>+D: Validate user
    D-->>-B: User data
    B->>B: Generate JWT token
    B-->>-F: Authentication response
    F-->>U: Login success
```

## Error Handling

```mermaid
flowchart TD
    A[Syntax Error Detected] --> B{Error Type}

    B -->|Missing Actor| C[Add Default Actor]
    B -->|Invalid Arrow| D[Fix Arrow Syntax]
    B -->|Malformed Message| E[Reconstruct Message]
    B -->|Timing Issue| F[Adjust Sequence Order]

    C --> G[Regenerate Code]
    D --> G
    E --> G
    F --> G

    G --> H[Validate Again]
    H --> I{Valid?}
    I -->|Yes| J[Success]
    I -->|No| K[Manual Review Required]

    style K fill:#ffebee
```

## Integration Points

### With SRS Generator

When generating SRS documents with diagrams enabled, sequence diagrams are automatically created for:

- User authentication flows
- API interaction patterns
- Data processing workflows
- Error handling scenarios

### With AI Conversation

Users can request sequence diagrams through natural language:

- "Generate a sequence diagram for user registration"
- "Show me the payment processing flow"
- "Create a diagram for the data synchronization process"

## Performance Considerations

- **Caching**: Generated diagrams are cached for 24 hours
- **Rate Limiting**: 10 sequence diagrams per minute per user
- **Complexity Limits**: Maximum 20 actors, 50 interactions per diagram
- **Timeout**: 30 seconds maximum generation time

## Quality Metrics

- **Syntax Validation**: 99.5% first-pass success rate
- **Actor Recognition**: 95% accuracy for standard business domains
- **Interaction Mapping**: 90% accuracy for complex flows
- **User Satisfaction**: Based on diagram usefulness ratings
