from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Import workflow graphs for AI-powered generation
from workflows import (
    srs_graph,
    class_diagram_graph,
    usecase_diagram_graph,
    activity_diagram_graph,
    wireframe_graph,
    stakeholder_register_graph,
    high_level_requirements_graph,
    requirements_management_plan_graph,
    business_case_graph,
    scope_statement_graph,
    product_roadmap_graph,
    feasibility_study_graph,
    cost_benefit_analysis_graph,
    risk_register_graph,
    compliance_graph
)

# Logging setup
import logging

# subprocess imports
import asyncio
from contextlib import asynccontextmanager
from services.mermaid_validator.subprocess_manager import MermaidSubprocessManager

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup:
        - Check if validator service is available
        - Log validator status

    Shutdown:
        - Cleanup if needed
    """
    # Startup - Check validator availability
    logger.info("Checking Mermaid validator service...")
    validator = MermaidSubprocessManager()

    # Wait for validator to be ready (retries if fail)
    max_retries = 30
    validator_ready = False
    for i in range(max_retries):
        if await validator.health_check():
            logger.info("✅ Mermaid validator service is ready")
            validator_ready = True
            break
        logger.info(f"⏳ Waiting for validator to be ready... ({i+1}/{max_retries})")
        await asyncio.sleep(1)
    
    if not validator_ready:
        logger.warning("⚠️ Validator not ready, diagram validation may fail")
    
    # Close the health check validator instance
    await validator.close()

    yield

    # Shutdown
    logger.info("AI Service shutting down...")

app = FastAPI(
    title="AI Service - BA Copilot",
    description="AI service for supporting Planning, Analysis, and Design phases in SDLC.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AIRequest(BaseModel):
    message: str
    content_id: Optional[str] = None
    storage_paths: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Create SRS for hotel management system",
                "content_id": "123e4567-e89b-12d3-a456-426614174000",
                "storage_paths": ["folder/file1.txt", "folder/file2.pdf"]
            }
        }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "BA Copilot AI Service",
        "version": "1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    openrouter_api_key = os.getenv("OPEN_ROUTER_API_KEY", "")
    return {
        "status": "healthy",
        "openrouter_api_configured": bool(openrouter_api_key)
    }

@app.post("/api/v1/srs/generate")
async def generate_srs(req: AIRequest):
    """
    Generate Software Requirements Specification (SRS) document.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with SRS data

    Example response:
        {
            "type": "srs",
            "response": {
                "title": "...",
                "functional_requirements": "...",
                "non_functional_requirements": "...",
                "detail": "..."
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        # Invoke SRS workflow
        result = srs_graph.invoke(state)
        return {"type": "srs", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SRS: {str(e)}"
        )

@app.post("/api/v1/generate/class-diagram")
async def generate_class_diagram(req: AIRequest):
    """
    Generate UML Class Diagram in Mermaid markdown format.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with class diagram data

    Example response:
        {
            "type": "diagram",
            "response": {
                "type": "class_diagram",
                "detail": "```mermaid\\nclassDiagram\\n...```"
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        # Invoke Class Diagram workflow
        result = class_diagram_graph.invoke(state)
        return {"type": "diagram", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating class diagram: {str(e)}"
        )

@app.post("/api/v1/generate/usecase-diagram")
async def generate_usecase_diagram(req: AIRequest):
    """
    Generate UML Use Case Diagram in Mermaid markdown format.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with use case diagram data

    Example response:
        {
            "type": "diagram",
            "response": {
                "type": "usecase_diagram",
                "detail": "```mermaid\\ngraph TD\\n...```"
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        # Invoke Use Case Diagram workflow
        result = usecase_diagram_graph.invoke(state)
        return {"type": "diagram", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating use case diagram: {str(e)}"
        )

@app.post("/api/v1/generate/activity-diagram")
async def generate_activity_diagram(req: AIRequest):
    """
    Generate UML Activity Diagram in Mermaid markdown format.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with activity diagram data

    Example response:
        {
            "type": "diagram",
            "response": {
                "type": "activity_diagram",
                "detail": "```mermaid\\ngraph TD\\n...```"
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        # Invoke Activity Diagram workflow
        result = activity_diagram_graph.invoke(state)
        return {"type": "diagram", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating activity diagram: {str(e)}"
        )

@app.post("/api/v1/wireframe/generate")
async def generate_wireframe(req: AIRequest):
    """
    Generate wireframe/UI mockup.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with wireframe data

    Example response:
        {
            "type": "wireframe",
            "response": {
                "figma_link": "https://...",
                "editable": true,
                "description": "..."
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        # Invoke Wireframe workflow
        result = wireframe_graph.invoke(state)
        return {"type": "wireframe", "response": result["response"]}

    except Exception as e:
        print("WIREFRAME ERROR FROM MAIN.PY: ", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating wireframe: {str(e)}"
        )

# Planning Document Services

@app.post("/api/v1/generate/stakeholder-register")
async def generate_stakeholder_register(req: AIRequest):
    """
    Generate Stakeholder Register document.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with stakeholder register data

    Example response:
        {
            "type": "stakeholder-register",
            "response": {
                "title": "Stakeholder Register - Project Name",
                "content": "# Stakeholder Register\n\n..."
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        result = stakeholder_register_graph.invoke(state)
        return {"type": "stakeholder-register", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating stakeholder register: {str(e)}"
        )

@app.post("/api/v1/generate/high-level-requirements")
async def generate_high_level_requirements(req: AIRequest):
    """
    Generate High-Level Requirements document.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with high-level requirements data

    Example response:
        {
            "type": "high-level-requirements",
            "response": {
                "title": "High-Level Requirements - Project Name",
                "content": "# High-Level Requirements\n\n..."
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        result = high_level_requirements_graph.invoke(state)
        return {"type": "high-level-requirements", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating high-level requirements: {str(e)}"
        )

@app.post("/api/v1/generate/requirements-management-plan")
async def generate_requirements_management_plan(req: AIRequest):
    """
    Generate Requirements Management Plan document.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with requirements management plan data

    Example response:
        {
            "type": "requirements-management-plan",
            "response": {
                "title": "Requirements Management Plan - Project Name",
                "content": "# Requirements Management Plan\n\n..."
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        result = requirements_management_plan_graph.invoke(state)
        return {"type": "requirements-management-plan", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating requirements management plan: {str(e)}"
        )

@app.post("/api/v1/generate/business-case")
async def generate_business_case(req: AIRequest):
    """
    Generate Business Case document with cost-benefit analysis and ROI projections.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with business case document data

    Example response:
        {
            "type": "business-case",
            "response": {
                "title": "Business Case - Project Name",
                "content": "# Business Case Document\n\n..."
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        result = business_case_graph.invoke(state)
        return {"type": "business-case", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating business case: {str(e)}"
        )

@app.post("/api/v1/generate/scope-statement")
async def generate_scope_statement(req: AIRequest):
    """
    Generate Scope Statement document defining project scope, deliverables, and boundaries.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with scope statement document data

    Example response:
        {
            "type": "scope-statement",
            "response": {
                "title": "Scope Statement - Project Name",
                "content": "# Scope Statement\n\n..."
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        result = scope_statement_graph.invoke(state)
        return {"type": "scope-statement", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating scope statement: {str(e)}"
        )

@app.post("/api/v1/generate/product-roadmap")
async def generate_product_roadmap(req: AIRequest):
    """
    Generate Product Roadmap diagram showing timeline and milestones.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with product roadmap diagram (Mermaid gantt chart)

    Example response:
        {
            "type": "diagram",
            "response": {
                "type": "product_roadmap",
                "detail": "```mermaid\\ngantt\\n...```"
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        result = product_roadmap_graph.invoke(state)
        return {"type": "diagram", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating product roadmap: {str(e)}"
        )

@app.post("/api/v1/generate/feasibility-study")
async def generate_feasibility_study(req: AIRequest):
    """
    Generate Feasibility Study Report analyzing technical, operational, economic, schedule, and legal feasibility.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with feasibility study document data

    Example response:
        {
            "type": "feasibility-study",
            "response": {
                "title": "Feasibility Study - Project Name",
                "executive_summary": "...",
                "technical_feasibility": "...",
                "operational_feasibility": "...",
                "economic_feasibility": "...",
                "schedule_feasibility": "...",
                "legal_feasibility": "...",
                "detail": "..."
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        result = feasibility_study_graph.invoke(state)
        return {"type": "feasibility-study", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating feasibility study: {str(e)}"
        )

@app.post("/api/v1/generate/cost-benefit-analysis")
async def generate_cost_benefit_analysis(req: AIRequest):
    """
    Generate Cost-Benefit Analysis document with ROI, NPV, and payback period calculations.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with cost-benefit analysis document data

    Example response:
        {
            "type": "cost-benefit-analysis",
            "response": {
                "title": "Cost-Benefit Analysis - Project Name",
                "executive_summary": "...",
                "cost_analysis": "...",
                "benefit_analysis": "...",
                "roi_calculation": "...",
                "npv_analysis": "...",
                "payback_period": "...",
                "detail": "..."
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        result = cost_benefit_analysis_graph.invoke(state)
        return {"type": "cost-benefit-analysis", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating cost-benefit analysis: {str(e)}"
        )

@app.post("/api/v1/generate/risk-register")
async def generate_risk_register(req: AIRequest):
    """
    Generate Risk Register document with comprehensive risk identification, assessment, and mitigation planning.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with risk register document data

    Example response:
        {
            "type": "risk-register",
            "response": {
                "title": "Risk Register - Project Name",
                "executive_summary": "...",
                "risk_identification": "...",
                "risk_assessment": "...",
                "mitigation_strategies": "...",
                "contingency_plans": "...",
                "detail": "..."
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        result = risk_register_graph.invoke(state)
        return {"type": "risk-register", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating risk register: {str(e)}"
        )

@app.post("/api/v1/generate/compliance")
async def generate_compliance(req: AIRequest):
    """
    Generate Compliance document analyzing legal and regulatory compliance requirements.

    Args:
        req (AIRequest): Request body containing message, content_id, storage_paths

    Returns:
        dict: Response with compliance document data

    Example response:
        {
            "type": "compliance",
            "response": {
                "title": "Compliance Document - Project Name",
                "executive_summary": "...",
                "regulatory_requirements": "...",
                "legal_requirements": "...",
                "compliance_status": "...",
                "recommendations": "...",
                "detail": "..."
            }
        }
    """
    try:
        # Handle empty string as None for content_id
        effective_content_id = req.content_id if req.content_id and req.content_id.strip() else None

        # Prepare state for workflow
        state = {
            "user_message": req.message,
            "content_id": effective_content_id,
            "storage_paths": req.storage_paths or []
        }

        result = compliance_graph.invoke(state)
        return {"type": "compliance", "response": result["response"]}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating compliance document: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
