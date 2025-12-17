# models/hld_tech.py
from pydantic import BaseModel

class HLDTechResponse(BaseModel):
    """Response model for Tech Stack Selection document"""
    title: str
    executive_summary: str
    frontend_technologies: str
    backend_technologies: str
    database_selection: str
    infrastructure_tools: str
    justification: str
    alternatives_considered: str
    detail: str

class HLDTechOutput(BaseModel):
    """Output wrapper for Tech Stack Selection"""
    type: str = "hld-tech"
    response: HLDTechResponse
