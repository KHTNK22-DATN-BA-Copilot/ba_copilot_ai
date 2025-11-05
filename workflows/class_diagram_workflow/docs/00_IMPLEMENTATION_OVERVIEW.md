# Mermaid Validation with MCP Server - Implementation Overview

## 📋 Table of Contents

This implementation guide is split into logical, commit-based sections:

1. **[01_DEPENDENCIES_SETUP.md](./01_DEPENDENCIES_SETUP.md)** - Installing and configuring dependencies
2. **[02_MCP_SERVER_SETUP.md](./02_MCP_SERVER_SETUP.md)** - Setting up the MCP server infrastructure
3. **[03_DOCKER_CONFIGURATION.md](./03_DOCKER_CONFIGURATION.md)** - Docker and docker-compose configuration
4. **[04_VALIDATION_LOGIC.md](./04_VALIDATION_LOGIC.md)** - Implementing validation nodes in LangGraph
5. **[05_INTEGRATION_TESTING.md](./05_INTEGRATION_TESTING.md)** - Comprehensive testing strategy
6. **[06_DEPLOYMENT_VERIFICATION.md](./06_DEPLOYMENT_VERIFICATION.md)** - Final deployment and verification

## 🎯 Implementation Goals

### Core Objectives

1. **Validate Mermaid Diagrams**: Ensure generated Mermaid code from LLM is syntactically correct
2. **MCP Integration**: Seamlessly integrate MCP server (`@rtuin/mcp-mermaid-validator`) with FastAPI application
3. **Robust Error Handling**: Gracefully handle validation failures with retry logic
4. **Production-Ready**: Ensure solution works in Docker containers and local development

### Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│                    (ba_copilot_ai)                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         LangGraph Class Diagram Workflow            │    │
│  │                                                      │    │
│  │  ┌──────────────┐      ┌──────────────────┐       │    │
│  │  │   Generate   │─────▶│    Validate       │       │    │
│  │  │   Diagram    │      │    Mermaid        │       │    │
│  │  │   (LLM)      │      │  (MCP Server)     │       │    │
│  │  └──────────────┘      └──────────────────┘       │    │
│  │                               │                     │    │
│  │                               ▼                     │    │
│  │                        ┌──────────────┐            │    │
│  │                        │   Retry/Fix  │            │    │
│  │                        │   (if error) │            │    │
│  │                        └──────────────┘            │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ HTTP/JSON-RPC
                       ▼
          ┌─────────────────────────────┐
          │      MCP Server             │
          │  (Node.js Process)          │
          │                             │
          │  @rtuin/mcp-mermaid-       │
          │  validator                  │
          │                             │
          │  - Validates Mermaid syntax │
          │  - Returns errors/success   │
          └─────────────────────────────┘
```

## 🔑 Key Design Decisions

### 1. MCP Server as Sidecar Process

**Decision**: Run MCP server as a separate process alongside FastAPI

**Rationale**:
- **Separation of Concerns**: Node.js-based MCP server runs independently from Python FastAPI
- **Process Isolation**: Failures in one don't crash the other
- **Technology Flexibility**: Leverage best-in-class tools (Node.js for MCP, Python for AI workflows)

**Trade-offs**:
- ✅ Better fault tolerance
- ✅ Independent scaling
- ❌ Additional process management complexity
- ❌ Network overhead (minimal for localhost)

### 2. HTTP/JSON-RPC Communication

**Decision**: Use HTTP-based JSON-RPC protocol for Python ↔ MCP server communication

**Rationale**:
- **Standard Protocol**: MCP servers use JSON-RPC 2.0 specification
- **Language Agnostic**: Easy to implement client in Python
- **Debugging Friendly**: Can inspect requests/responses with standard tools

**Implementation**:
```python
# Direct HTTP requests to MCP server
response = requests.post(
    "http://localhost:3000",
    json={
        "jsonrpc": "2.0",
        "method": "validate_mermaid",
        "params": {"code": mermaid_code},
        "id": 1
    }
)
```

### 3. Validation as LangGraph Node

**Decision**: Add validation as a discrete node in the LangGraph workflow

**Rationale**:
- **Observability**: Clear visibility into validation step
- **Retry Logic**: Easy to implement conditional edges for retry
- **Testing**: Can unit test validation node independently
- **State Management**: LangGraph manages state transitions naturally

**Graph Structure**:
```
[Generate] → [Validate] → [END]
              ↓ (if error)
            [Retry/Fix] → [Validate]
```

### 4. Docker Multi-Container Architecture

**Decision**: Run MCP server and FastAPI in separate containers

**Rationale**:
- **Best Practice**: One process per container (Docker philosophy)
- **Independent Updates**: Update MCP server without rebuilding Python image
- **Resource Management**: Separate CPU/memory limits
- **Healthchecks**: Independent health monitoring

**Alternative Considered**: Single container with supervisord
- ❌ Violates single-process principle
- ❌ More complex failure scenarios
- ✅ Simpler deployment (only one benefit, not worth it)

### 5. Graceful Degradation Strategy

**Decision**: If MCP server unavailable, return unvalidated diagram with warning

**Rationale**:
- **Availability**: Don't block core functionality due to validation service
- **User Experience**: Better to get unvalidated diagram than error
- **Monitoring**: Log warnings for ops team to investigate

**Implementation**:
```python
try:
    validated_code = validate_mermaid(code)
    return {"code": validated_code, "validated": True}
except MCPServerUnavailable:
    logger.warning("MCP server unavailable, returning unvalidated")
    return {"code": code, "validated": False, "warning": "Not validated"}
```

## 🧩 Component Breakdown

### Python Components (ba_copilot_ai)

| Component | Purpose | Files |
|-----------|---------|-------|
| **MCP Client** | Communicate with MCP server | `services/mcp_client.py` |
| **Validation Node** | LangGraph node for validation | `workflows/class_diagram_workflow/validation.py` |
| **Updated Workflow** | Integrate validation into graph | `workflows/class_diagram_workflow/workflow.py` |
| **Models** | Add validation result models | `models/diagram.py` |
| **Tests** | Unit and integration tests | `tests/test_class_diagram_validation.py` |

### Node.js Components (MCP Server)

| Component | Purpose | Location |
|-----------|---------|----------|
| **MCP Server** | Validates Mermaid syntax | Docker container |
| **Package** | `@rtuin/mcp-mermaid-validator` | npm package |
| **Process Manager** | Ensure server stays running | Docker healthcheck |

### Infrastructure Components

| Component | Purpose | Files |
|-----------|---------|-------|
| **Docker Services** | Container orchestration | `docker-compose.yml` |
| **Dockerfiles** | Build instructions | `Dockerfile`, `Dockerfile.mcp` |
| **Environment** | Configuration | `.env`, `.env.example` |
| **Health Checks** | Service monitoring | Docker healthcheck, `/health` endpoint |

## 📊 Implementation Metrics

### Commit Structure

Each phase produces **1-2 meaningful commits**:

1. **Dependencies**: `feat: add MCP client dependencies and Python packages`
2. **MCP Server**: `feat: configure MCP server with Docker integration`
3. **Docker Config**: `chore: update Docker configs for MCP server sidecar`
4. **Validation Logic**: `feat: implement Mermaid validation node in LangGraph`
5. **Tests**: `test: add comprehensive tests for diagram validation`
6. **Deployment**: `chore: verify full stack deployment and integration`

### Testing Coverage Targets

- **Unit Tests**: 90%+ coverage for validation logic
- **Integration Tests**: End-to-end workflow validation
- **Docker Tests**: Container health and communication
- **Load Tests**: Validate under concurrent requests

## 🔍 Core Concepts Explained

### Model Context Protocol (MCP)

**What is MCP?**
- Protocol for connecting AI applications to external tools/data sources
- Uses JSON-RPC 2.0 for communication
- Server exposes "tools" that clients can invoke
- Designed for LLM integration patterns

**Why MCP for Mermaid Validation?**
- Existing, battle-tested validator: `@rtuin/mcp-mermaid-validator`
- Standard interface for validation operations
- Future extensibility (add more diagram validators)
- Community support and maintenance

**MCP Request Flow**:
```
1. Client sends JSON-RPC request:
   {
     "jsonrpc": "2.0",
     "method": "tools/call",
     "params": {
       "name": "validate_mermaid",
       "arguments": {"code": "graph TD\nA-->B"}
     },
     "id": 1
   }

2. Server validates and responds:
   {
     "jsonrpc": "2.0",
     "result": {
       "content": [{"type": "text", "text": "Valid"}]
     },
     "id": 1
   }
```

### LangGraph State Management

**Why LangGraph for Validation?**
- **State Persistence**: Maintains diagram generation state across nodes
- **Conditional Routing**: Easy to implement retry logic based on validation results
- **Observability**: Built-in tracing and debugging
- **Error Handling**: Graceful error propagation

**State Design**:
```python
class ClassDiagramState(TypedDict):
    user_message: str           # Original user request
    raw_diagram: str            # LLM-generated Mermaid code
    validation_result: dict     # MCP validation response
    validated_diagram: str      # Final validated code
    retry_count: int           # Number of retry attempts
    response: dict             # Final output
```

**Node Responsibilities**:
1. **generate_class_diagram**: Call LLM, produce raw Mermaid
2. **validate_diagram**: Send to MCP server, check syntax
3. **fix_diagram** (conditional): If invalid, ask LLM to fix
4. **format_response**: Prepare final output

### Docker Networking

**Container Communication Strategy**:
```yaml
services:
  ai-service:
    networks:
      - ba-network
    depends_on:
      - mcp-server
    environment:
      - MCP_SERVER_URL=http://mcp-server:3000

  mcp-server:
    networks:
      - ba-network
    expose:
      - "3000"  # Internal only, not published to host

networks:
  ba-network:
    driver: bridge
```

**Key Points**:
- Services communicate via Docker network DNS (`http://mcp-server:3000`)
- MCP server port not exposed to host (security)
- Health checks ensure startup order
- Restart policies handle failures

## 🚀 Success Criteria

### Functional Requirements
- ✅ MCP server starts with application
- ✅ Generated Mermaid diagrams are validated
- ✅ Invalid diagrams trigger retry with LLM fix
- ✅ Validation results included in API response
- ✅ System works in both Docker and local dev

### Non-Functional Requirements
- ✅ Validation adds <500ms latency
- ✅ Graceful degradation if MCP server unavailable
- ✅ 90%+ test coverage
- ✅ Clear error messages for debugging
- ✅ Monitoring/logging for validation failures

## 📚 Prerequisites

Before starting implementation, ensure:

- [x] Python 3.11+ installed
- [x] Node.js 18+ installed (for local MCP testing)
- [x] Docker and Docker Compose installed
- [x] Virtual environment activated: `.venv`
- [x] OpenRouter API key configured
- [x] PostgreSQL database running

## 🔗 External References

### MCP Resources
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [@rtuin/mcp-mermaid-validator Package](https://www.npmjs.com/package/@rtuin/mcp-mermaid-validator)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### Mermaid Resources
- [Mermaid.js Documentation](https://mermaid.js.org/)
- [Mermaid Class Diagram Syntax](https://mermaid.js.org/syntax/classDiagram.html)
- [Mermaid Live Editor](https://mermaid.live/) (for manual testing)

### LangGraph Resources
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [State Management Guide](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)
- [Conditional Edges Tutorial](https://langchain-ai.github.io/langgraph/how-tos/branching/)

### Docker Resources
- [Docker Multi-Container Apps](https://docs.docker.com/compose/)
- [Docker Networking](https://docs.docker.com/network/)
- [Docker Health Checks](https://docs.docker.com/engine/reference/builder/#healthcheck)

## 🗺️ Navigation

**Start Implementation**: [01_DEPENDENCIES_SETUP.md](./01_DEPENDENCIES_SETUP.md) →

---

**Last Updated**: November 5, 2025  
**Version**: 1.0.0  
**Author**: Principal AI Engineering Team
