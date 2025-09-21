# Use Case Diagram Generation Workflow

## Overview

The Use Case Diagram Generator creates UML use case diagrams from user stories, requirements, or system descriptions. This service focuses on modeling system functionality from the user's perspective, showing actors, use cases, and their relationships.

## Core Workflow

```mermaid
flowchart TD
    A[Use Case Diagram Request] --> B[Input Validation]
    B --> C[Requirements Analysis]
    C --> D[Actor Identification]
    D --> E[Use Case Extraction]
    E --> F[Relationship Mapping]

    F --> G[LLM Processing]
    G --> H[Generate Mermaid Code]
    H --> I[Validate Use Case Structure]

    I --> J{Valid Use Cases?}
    J -->|No| K[Use Case Analysis]
    K --> L[Regenerate with Corrections]
    L --> H

    J -->|Yes| M[Apply Use Case Styling]
    M --> N[Render Preview]
    N --> O[Store Diagram]
    O --> P[Return Response]

    style G fill:#fff3e0
    style H fill:#e8f5e8
    style N fill:#e1f5fe
```

## Actor Classification Process

```mermaid
flowchart TD
    A[System Description] --> B[Entity Extraction]
    B --> C{Entity Analysis}

    C -->|Person/Role| D[Primary Actor]
    C -->|External System| E[Secondary Actor]
    C -->|Time/Event| F[Temporal Actor]

    D --> G[Actor Categorization]
    E --> G
    F --> G

    G --> H{Actor Type}
    H -->|Human User| I[User Actor]
    H -->|Administrator| J[Admin Actor]
    H -->|System/Service| K[System Actor]
    H -->|External API| L[External Actor]

    I --> M[Actor Registry]
    J --> M
    K --> M
    L --> M

    M --> N[Define Actor Attributes]
    N --> O[Actor Relationships]

    style M fill:#e8f5e8
```

## Use Case Identification

```mermaid
flowchart TD
    A[Functional Requirements] --> B[Action Verb Extraction]
    B --> C[Goal Identification]
    C --> D{Use Case Scope}

    D -->|Single Action| E[Elementary Use Case]
    D -->|Multiple Steps| F[Complex Use Case]
    D -->|System Function| G[System Use Case]

    E --> H[Use Case Details]
    F --> H
    G --> H

    H --> I[Preconditions]
    I --> J[Main Flow]
    J --> K[Alternative Flows]
    K --> L[Postconditions]

    L --> M[Use Case Validation]
    M --> N[Use Case Registry]

    style N fill:#e1f5fe
```

## Relationship Mapping

```mermaid
flowchart TD
    A[Actors & Use Cases] --> B{Relationship Type}

    B -->|Direct Interaction| C[Association]
    B -->|Shared Behavior| D[Include Relationship]
    B -->|Optional Behavior| E[Extend Relationship]
    B -->|Similar Actors| F[Generalization]

    C --> G[Relationship Registry]
    D --> G
    E --> G
    F --> G

    G --> H[Validate Relationships]
    H --> I{Valid Structure?}
    I -->|Yes| J[Generate Connections]
    I -->|No| K[Fix Relationships]
    K --> H

    J --> L[Diagram Structure]

    style L fill:#e8f5e8
```

## Detailed Processing Flow

```mermaid
sequenceDiagram
    participant User as User
    participant API as Diagram API
    participant Analyzer as Requirements Analyzer
    participant Extractor as Use Case Extractor
    participant LLM as LLM Service
    participant Validator as Use Case Validator
    participant Renderer as Diagram Renderer
    participant Storage as Database

    User->>API: POST /diagrams/usecase/generate
    API->>Analyzer: Analyze requirements text

    Analyzer->>Analyzer: Extract functional requirements
    Analyzer->>Analyzer: Identify user goals
    Analyzer->>Extractor: Extract actors and use cases

    Extractor->>Extractor: Classify actors
    Extractor->>Extractor: Define use cases
    Extractor->>Extractor: Map relationships

    Extractor->>LLM: Generate use case diagram
    Note over LLM: Process: actors, use cases, relationships

    LLM->>Validator: Validate use case structure
    Validator->>Validator: Check actor consistency
    Validator->>Validator: Verify relationship validity

    alt Valid Use Case Model
        Validator->>Renderer: Generate diagram
        Renderer->>Storage: Store diagram
        Storage->>API: Return diagram ID
        API->>User: Return use case response
    else Invalid Use Case Model
        Validator->>LLM: Request model corrections
        LLM->>Validator: Regenerate with fixes
    end
```

## Use Case Relationship Types

### Include Relationships

```mermaid
graph TB
    subgraph "E-commerce System"
        UC1[Place Order]
        UC2[Validate Payment]
        UC3[Update Inventory]
    end

    Customer --> UC1
    UC1 -.->|includes| UC2
    UC1 -.->|includes| UC3

    style UC1 fill:#e3f2fd
    style UC2 fill:#f3e5f5
    style UC3 fill:#f3e5f5
```

### Extend Relationships

```mermaid
graph TB
    subgraph "Banking System"
        UC1[Withdraw Cash]
        UC2[Print Receipt]
        UC3[Send SMS Notification]
    end

    Customer --> UC1
    UC2 -.->|extends| UC1
    UC3 -.->|extends| UC1

    style UC1 fill:#e3f2fd
    style UC2 fill:#fff3e0
    style UC3 fill:#fff3e0
```

### Actor Generalization

```mermaid
graph TB
    subgraph "System Actors"
        A1[Admin]
        A2[Super Admin]
        A3[Regular User]
        A4[User]
    end

    subgraph "Use Cases"
        UC1[Manage Users]
        UC2[View Reports]
        UC3[Login]
    end

    A2 --> A1
    A3 --> A4
    A1 --> UC1
    A1 --> UC2
    A4 --> UC3

    style A1 fill:#e8f5e8
    style A4 fill:#e8f5e8
```

## Sample Input/Output

### Input Example

```json
{
  "title": "E-commerce Use Cases",
  "description": "E-commerce platform user interactions and admin functions",
  "actors": [
    {
      "name": "Customer",
      "type": "primary",
      "description": "End user purchasing products"
    },
    {
      "name": "Admin",
      "type": "primary",
      "description": "System administrator"
    }
  ],
  "use_cases": [
    {
      "name": "Browse Products",
      "actor": "Customer",
      "description": "Customer can browse product catalog"
    },
    {
      "name": "Manage Inventory",
      "actor": "Admin",
      "description": "Admin can manage product inventory"
    }
  ]
}
```

### Generated Mermaid Output

```mermaid
graph TB
    subgraph "E-commerce System"
        UC1[Browse Products]
        UC2[Add to Cart]
        UC3[Checkout]
        UC4[Manage Inventory]
        UC5[Process Orders]
    end

    Customer --> UC1
    Customer --> UC2
    Customer --> UC3
    Admin --> UC4
    Admin --> UC5

    UC3 -.->|includes| UC6[Validate Payment]
    UC3 -.->|includes| UC7[Update Inventory]

    style Customer fill:#e3f2fd
    style Admin fill:#e8f5e8
    style UC1 fill:#f3e5f5
    style UC4 fill:#fff3e0
```

## Use Case Validation Rules

```mermaid
flowchart TD
    A[Generated Use Case Model] --> B[Validation Engine]
    B --> C{Validation Rules}

    C --> D[Actor-Use Case Association]
    C --> E[Include/Extend Consistency]
    C --> F[Circular Relationship Check]
    C --> G[Actor Role Validation]
    C --> H[Use Case Granularity]

    D --> I{All Rules Pass?}
    E --> I
    F --> I
    G --> I
    H --> I

    I -->|Yes| J[Valid Use Case Model]
    I -->|No| K[Generate Corrections]
    K --> L[Apply Fixes]
    L --> A

    style J fill:#e8f5e8
    style K fill:#ffebee
```

## Error Handling

```mermaid
flowchart TD
    A[Use Case Error] --> B{Error Type}

    B -->|Missing Actor| C[Actor Inference]
    B -->|Vague Use Case| D[Use Case Refinement]
    B -->|Invalid Relationship| E[Relationship Correction]
    B -->|Scope Issues| F[Granularity Adjustment]

    C --> G[Auto-Fix Engine]
    D --> G
    E --> G
    F --> G

    G --> H{Fix Applied?}
    H -->|Yes| I[Regenerate Model]
    H -->|No| J[Flag for Review]

    I --> K[Success]
    J --> L[Manual Intervention]

    style K fill:#e8f5e8
    style L fill:#ffebee
```

## Context-Aware Generation

```mermaid
flowchart TD
    A[System Context] --> B{Domain Type}

    B -->|E-commerce| C[E-commerce Templates]
    B -->|Banking| D[Banking Templates]
    B -->|Healthcare| E[Healthcare Templates]
    B -->|Education| F[Education Templates]
    B -->|Generic| G[Generic Templates]

    C --> H[Domain-Specific Actors]
    D --> H
    E --> H
    F --> H
    G --> H

    H --> I[Common Use Case Patterns]
    I --> J[Relationship Templates]
    J --> K[Generate Context-Aware Model]

    style K fill:#e1f5fe
```

## Integration Points

### With SRS Generator

Use case diagrams are automatically generated for:

- Functional requirements sections
- User story collections
- System capability overviews
- Stakeholder interaction models

### With AI Conversation

Users can request use case diagrams through natural language:

- "Show me the use cases for an online banking system"
- "Generate use cases for customer management"
- "Create a use case diagram for our inventory system"

## Performance Considerations

- **Actor Limits**: Maximum 20 actors per diagram
- **Use Case Limits**: Maximum 40 use cases per diagram
- **Relationship Limits**: Maximum 100 relationships per diagram
- **Processing Time**: 20-60 seconds depending on complexity

## Quality Metrics

- **Actor Identification**: 91% accuracy for business domains
- **Use Case Extraction**: 87% accuracy for functional requirements
- **Relationship Mapping**: 83% accuracy for complex relationships
- **Model Completeness**: 89% coverage of functional requirements
