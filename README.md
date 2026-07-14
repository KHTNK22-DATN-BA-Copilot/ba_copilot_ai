<div align="center">
<h2> 🤖 BA Copilot - AI Service </h2>

An AI-powered microservice that assists Business Analysts by automatically generating documentation across the Planning, Analysis, and Design phases of the SDLC.

<img src="docs/images/architecture.png" alt="AI Service Architecture" width="800"/>
  
![Python](https://img.shields.io/badge/Python_3.11-black?style=for-the-badge&logo=python&logoColor=3776AB)
![FastAPI](https://img.shields.io/badge/FastAPI-black?style=for-the-badge&logo=fastapi&logoColor=009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-black?style=for-the-badge&logo=postgresql&logoColor=4169E1)
![Docker](https://img.shields.io/badge/Docker-black?style=for-the-badge&logo=docker&logoColor=2496ED)
![Supabase](https://img.shields.io/badge/Supabase-black?style=for-the-badge&logo=supabase&logoColor=3ECF8E)

</div>

## 📘 Table of Contents

* [Key Features](#key-features)
* [Technologies Used](#technologies-used)
* [Architecture](#architecture)
* [Getting Started](#getting-started)
* [API Endpoints](#api-endpoints)
* [Response Format](#response-format)
* [Project Structure](#project-structure)
* [Notes](#notes)
* [Troubleshooting](#troubleshooting)

---

## Key Features
 
- **Diverse BA Document Generation**: Generates SRS, Business Case, Scope Statement, Feasibility Study, Risk Register, HLD/LLD, RTM, and many more (~26 document types).
- **UML Diagram Generation (Mermaid)**: Class Diagram, Use Case Diagram, Activity Diagram.
- **UI/UX Generation (HTML/CSS)**: Wireframes, Mockups, Prototypes.
- **RAG (Retrieval-Augmented Generation)**: Retrieves relevant context via semantic search on `pgvector`, filtering by `project_id` and dependent document types.
- **Metadata Extraction**: Analyzes a Markdown document to detect embedded BA document types and their corresponding line numbers.
- **Multi-Provider + BYOK (Bring Your Own Key)**: Supports OpenRouter (default), OpenAI, Google Gemini, and Anthropic. Allows users to pass their own API keys per request.

## Technologies Used
 
| Technology | Role in Project |
|-----------|---------------------|
| **Python 3.11** | Primary programming language for the entire service |
| **FastAPI** | Web framework to expose HTTP endpoints and auto-generate Swagger/ReDoc |
| **Pydantic** | Defining and validating request/response schemas |
| **LangChain** | LLM integration layer: builds chat models by provider, invokes models, standardizes messages |
| **LangGraph** | Orchestrates workflows as **stateful graphs** — each document type is a graph composed of a sequence of nodes |
| **Tiktoken** | Counts tokens (`cl100k_base`) to manage token budgets when building chat history context |
| **Supabase** | (1) Vector DB `pgvector` to store `rag_chunks` for RAG; (2) Storage for uploaded files |
| **Embedding** | Converts user queries into vector embeddings (1536 dimensions) via OpenRouter Embeddings |
| **PostgreSQL + pgvector** | Stores embeddings and performs similarity search via the `match_rag_chunks` RPC |
| **SQLAlchemy** | Connects to and queries Postgres for the RAG layer |
| **httpx** | Calls External Backend APIs to retrieve chat history |
| **Docker / Docker Compose** | Containerization for the service and database |
 
**Supported LLM Providers:** OpenAI · OpenRouter · Google Gemini · Anthropic
 
## Architecture
 
*General Flow:*
 
```text
External Backend ──HTTP──► API Layer (FastAPI / Pydantic)
                                │
                                ▼
                        Context Builder
              ┌──────────────┬──────────────┬───────────────┐
              │ Chat History │ Supabase +   │ Embedding +   │
              │ (Backend API)│ pgvector     │ Tiktoken      │
              └──────────────┴──────────────┴───────────────┘
                                │  (context + token budget)
                                ▼
                     Pipeline Orchestration
              LangChain (prompt/chains) + LangGraph (stateful graph)
                     + Provider Router (model selection)
                                │
                                ▼
                          LLM Providers
                OpenAI · OpenRouter · Gemini · Anthropic
```
 
## Getting Started
 
### Prerequisites
 
- Docker & Docker Compose
- API key for at least one LLM provider (OpenRouter is used by default)
- (Optional) Supabase project for storage + pgvector

### Run the Project
 
#### 1. Clone the repository
 
```bash
git clone [https://github.com/KHTNK22-DATN-BA-Copilot/ba_copilot_ai.git](https://github.com/KHTNK22-DATN-BA-Copilot/ba_copilot_ai.git)
cd ba_copilot_ai
```
 
#### 2. Create the `.env` file from `.env.example`
 
```bash
cp .env.example .env
```
 
Open the `.env` file and fill in the required environment variables:
 
```env
# --- LLM Provider (Default: OpenRouter) ---
OPEN_ROUTER_API_KEY=your_openrouter_key
MODEL=anthropic/claude-haiku-4.5
OPENROUTER_REFERER=http://localhost:8000
OPENROUTER_TITLE=BA-Copilot
 
# Other providers (optional, used for BYOK / changing providers)
OPENAI_API_KEY=your_openai_key
GOOGLE_AI_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key
 
# --- Database (Postgres + pgvector) ---
DATABASE_URL=postgresql://postgres:postgres123@db:5432/bacopilot_db
# RAG_DATABASE_URL=  # if using a separate DB for RAG, defaults to DATABASE_URL
 
# --- Embedding ---
OPENROUTER_EMBEDDING_MODEL=text-embedding-3-small
 
# --- Backend API (to fetch chat history) ---
BACKEND_API_URL=http://localhost:8010
 
# --- Supabase Storage (Optional) ---
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_BUCKET=uploads
 
# --- Token budget ---
MAX_CONTEXT_TOKENS=100000
```
 
#### 3. Build the image and start containers using Docker
 
```bash
# Build image and start services (ai-service + postgres)
docker-compose up --build
 
# Or run in detached mode (background)
docker-compose up -d --build
```
 
The service will be available at `http://localhost:8000`. The bundled Postgres runs on port `5433` (mapped from `5432` inside the container).
 
#### 4. Health Check
 
```bash
curl http://localhost:8000/health
```
 
Expected response:
 
```json
{ "status": "healthy", "openrouter_api_configured": true }
```
 
#### Useful Docker Commands
 
```bash
docker-compose logs -f ai-service   # View logs
docker-compose down                 # Stop services
docker-compose down -v              # Stop and remove volumes (reset DB)
```
 
### (Optional) Run locally without Docker
 
```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
 
## API Endpoints
 
**Base URL:** `http://localhost:8000`
 
All document generation endpoints share the same `AIRequest` request body:
 
```json
{
  "message": "Generate an SRS for a hotel management system",
  "content_id": "123e4567-e89b-12d3-a456-426614174000",
  "project_id": 1,
  "document_format": "markdown"
}
```
 
You can dynamically pass the model/provider/API key per request via HTTP headers (BYOK):
`X-AI-Provider`, `X-AI-Model`, `X-AI-API-Key`.
 
### System
 
| Method | Endpoint | Description |
|--------|----------|-------|
| GET | `/` | Service information |
| GET | `/health` | Health check |
 
### Text Document Generation (Markdown)
 
| Method | Endpoint | Description |
|--------|----------|-------|
| POST | `/api/v1/srs/generate` | Generate SRS |
| POST | `/api/v1/generate/stakeholder-register` | Stakeholder Register |
| POST | `/api/v1/generate/high-level-requirements` | High-Level Requirements |
| POST | `/api/v1/generate/requirements-management-plan` | Requirements Management Plan |
| POST | `/api/v1/generate/business-case` | Business Case |
| POST | `/api/v1/generate/scope-statement` | Scope Statement |
| POST | `/api/v1/generate/product-roadmap` | Product Roadmap |
| POST | `/api/v1/generate/feasibility-study` | Feasibility Study |
| POST | `/api/v1/generate/cost-benefit-analysis` | Cost-Benefit Analysis |
| POST | `/api/v1/generate/risk-register` | Risk Register |
| POST | `/api/v1/generate/compliance` | Compliance |
| POST | `/api/v1/generate/rtm` | Requirements Traceability Matrix |
 
### HLD / LLD Design Document Generation
 
| Method | Endpoint | Description |
|--------|----------|-------|
| POST | `/api/v1/generate/hld-arch` | High-Level Architecture |
| POST | `/api/v1/generate/hld-cloud` | High-Level Cloud Design |
| POST | `/api/v1/generate/hld-tech` | High-Level Tech Stack |
| POST | `/api/v1/generate/lld-arch` | Low-Level Architecture |
| POST | `/api/v1/generate/lld-db` | Low-Level Database Design |
| POST | `/api/v1/generate/lld-api` | Low-Level API Design |
| POST | `/api/v1/generate/lld-pseudo` | Low-Level Pseudocode |
 
### UML Diagram Generation (Mermaid)
 
| Method | Endpoint | Description |
|--------|----------|-------|
| POST | `/api/v1/generate/class-diagram` | Class Diagram |
| POST | `/api/v1/generate/usecase-diagram` | Use Case Diagram |
| POST | `/api/v1/generate/activity-diagram` | Activity Diagram |
 
### UI/UX Generation (HTML/CSS)
 
| Method | Endpoint | Description |
|--------|----------|-------|
| POST | `/api/v1/generate/uiux-wireframe` | Wireframe |
| POST | `/api/v1/generate/uiux-mockup` | Mockup |
| POST | `/api/v1/generate/uiux-prototype` | Prototype |
 
### Metadata
 
| Method | Endpoint | Description |
|--------|----------|-------|
| POST | `/api/v1/metadata/extract` | Detect BA document types within a Markdown file and their line positions |
| GET | `/api/v1/metadata/document-types` | List of supported document types |
 
### API Documentation
 
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- [AI Provider Factory Guide](docs/AI_PROVIDER_FACTORY.md) — Multi-provider & BYOK configuration
- [API Specifications](AI_API_SPECS.md) — Endpoint details

### Example API Calls
 
```bash
# Generate SRS
curl -X POST http://localhost:8000/api/v1/srs/generate \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate an SRS for a library management system", "project_id": 1}'
 
# Generate Class Diagram
curl -X POST http://localhost:8000/api/v1/generate/class-diagram \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate a class diagram for a sales system", "project_id": 1}'
```
 
## Response Format
 
All document generation endpoints return a standardized JSON structure:
 
```json
{
  "type": "srs",
  "response": {
    "summary": "One-line summary",
    "content": "# Software Requirements Specification\n\n...",
    "status_code": 200
  }
}
```
 
- **Text Documents:** `content` is in Markdown.
- **Diagrams:** `content` contains a ```mermaid``` block.
- **UI/UX:** `content` is an object: `{ "html": "...", "css": "..." }`.

## Project Structure
 
```text
ba_copilot_ai/
├── main.py                     # FastAPI app + all endpoints + BYOK middleware
├── connect_model.py            # ModelClient + request-scoped config (ContextVar)
├── factory.py                  # Factory to build chat models by provider (BYOK + .env fallback)
├── response.py                 # Standardized success/error responses
├── constants/
│   └── docs_constraint.py      # Dependencies between document types (RAG filters)
├── models/                     # Pydantic models for each document type
├── services/
│   └── rag/                    # RAG: embeddings, retriever, supabase_client
├── utils/                      # context_builder, tokenizer (tiktoken), prompt_builder, parser
├── workflows/                  # Each document type = 1 LangGraph workflow
│   ├── base/                   # Shared state, document_generator, additional_rules
│   ├── nodes/                  # get_context_node, node_chat_history, get_content_file, node_ocr
│   ├── srs_workflow/
│   ├── class_diagram_workflow/
│   └── ...                     # ~26 workflows total
├── docs/                       # Architecture docs, sequence diagrams, RAG schemas
├── tests/                      # Pytest test suites
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```
 
## Notes
 
- The `.env` file contains sensitive information and is ignored by Git; `.env.example` serves as a template.
- Ensure `DATABASE_URL` points to a Postgres instance with the `pgvector` extension enabled, along with the `rag_chunks` table and `match_rag_chunks` RPC (see `docs/rag_schema.sql`).
- Chat history is retrieved from the Backend API (`BACKEND_API_URL`); if `content_id` is missing, this step is skipped.
- **BYOK (Bring Your Own Key):** When a client sends the `X-AI-API-Key` header, the service uses that key exclusively for that request without overwriting global environment variables.

## Troubleshooting
 
### Docker build fails
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```
 
### Port already in use
Change the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"
```
 
### API Key Errors
- Verify that the `.env` file is properly formatted and using the correct variable names for your active provider.
- Restart the container after making changes to the `.env` file.

### RAG returns empty results
- Check your Postgres connection and ensure the `pgvector` extension is enabled.
- Verify that the `rag_chunks` table contains embedding data for the corresponding `project_id`.
