# AI Conversation Manager Service Flow Diagram

## Overview

The AI Conversation Manager handles chat interactions between users and AI, maintaining conversation history and providing contextual responses.

## Primary Flow Diagram

```mermaid
flowchart TD
    A[User Sends Message] --> B{Session Exists?}
    B -->|No| C[Create New Session]
    B -->|Yes| D[Load Session Context]

    C --> E[Generate Session ID]
    E --> F[Initialize Conversation]
    F --> G[Store Initial Message]

    D --> H[Retrieve Conversation History]
    H --> G

    G --> I[Prepare Context for LLM]
    I --> J[Send to LLM Service]

    J --> K[LLM Processing]
    K --> L[Receive AI Response]

    L --> M[Post-process Response]
    M --> N[Store AI Message]
    N --> O[Update Session Metadata]

    O --> P[Return Response to User]
    P --> Q[Display in Chat Interface]

    Q --> R{User Action}
    R -->|Continue Chat| S[Send New Message]
    R -->|Export Chat| T[Generate Transcript]
    R -->|Delete Chat| U[Remove Session]
    R -->|Search History| V[Query Conversations]

    S --> B
```

## Session Management Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as Chat API
    participant SM as Session Manager
    participant CM as Context Manager
    participant LLM as LLM Service
    participant DB as Database

    U->>FE: Send message
    FE->>API: POST /conversations/{id}/send
    API->>SM: Validate session

    alt New Session
        SM->>DB: Create new conversation
    else Existing Session
        SM->>DB: Load conversation history
    end

    SM->>CM: Prepare message context
    CM->>CM: Build conversation context
    CM->>LLM: Send contextual prompt

    LLM->>LLM: Generate response
    LLM->>CM: Return AI response

    CM->>DB: Store user message
    CM->>DB: Store AI response

    CM->>API: Return response
    API->>FE: 200 OK with AI message
    FE->>U: Display AI response
```

## Context Management Flow

```mermaid
flowchart TD
    A[Incoming Message] --> B[Load Conversation History]
    B --> C{History Length Check}
    C -->|< Token Limit| D[Use Full History]
    C -->|> Token Limit| E[Apply Context Compression]

    E --> F[Summarize Old Messages]
    F --> G[Keep Recent Messages]
    G --> H[Maintain Context Continuity]

    D --> I[Build LLM Prompt]
    H --> I

    I --> J[Add System Instructions]
    J --> K[Add User Message]
    K --> L[Send to LLM]

    L --> M[Receive Response]
    M --> N[Extract Response Content]
    N --> O[Update Context Window]
    O --> P[Store in Session]
```

## Multi-LLM Routing Flow

```mermaid
graph TD
    A[User Message] --> B[Message Classification]
    B --> C{Message Type}

    C -->|Technical Query| D[Route to Technical LLM]
    C -->|Creative Request| E[Route to Creative LLM]
    C -->|General Chat| F[Route to General LLM]
    C -->|Code Generation| G[Route to Code LLM]

    D --> H[OpenAI GPT-4]
    E --> I[Claude-3]
    F --> J[General Purpose Model]
    G --> K[Code-Specialized Model]

    H --> L[Process Response]
    I --> L
    J --> L
    K --> L

    L --> M[Return to User]
```

## Error Handling and Fallback

```mermaid
flowchart TD
    A[Message Processing] --> B{LLM Service Status}
    B -->|Available| C[Send to Primary LLM]
    B -->|Unavailable| D[Check Fallback Services]

    D --> E{Fallback Available?}
    E -->|Yes| F[Route to Fallback LLM]
    E -->|No| G[Return Service Unavailable]

    C --> H{Response Received?}
    F --> H

    H -->|Yes| I[Validate Response]
    H -->|No| J[Timeout Handling]

    I -->|Valid| K[Return Response]
    I -->|Invalid| L[Request Retry]

    J --> M{Retry Count < 3?}
    M -->|Yes| N[Retry Request]
    M -->|No| O[Return Timeout Error]

    L --> M
    N --> C
```

## Real-time Communication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant WS as WebSocket
    participant API as Chat API
    participant LLM as LLM Service
    participant DB as Database

    U->>WS: Connect to chat session
    WS->>API: Establish connection

    U->>WS: Send message via WebSocket
    WS->>API: Forward message
    API->>LLM: Process message

    Note over API,LLM: Streaming response
    LLM-->>API: Partial response chunk 1
    API-->>WS: Stream chunk 1
    WS-->>U: Display partial response

    LLM-->>API: Partial response chunk 2
    API-->>WS: Stream chunk 2
    WS-->>U: Update response display

    LLM->>API: Final response complete
    API->>DB: Store complete conversation
    API->>WS: Response complete signal
    WS->>U: Finalize response display
```
