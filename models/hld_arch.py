# models/hld_arch.py
from pydantic import BaseModel

class HLDArchResponse(BaseModel):
    """Response model for High-Level Design Architecture Diagram"""
    type: str
    detail: str

class HLDArchOutput(BaseModel):
    """Output wrapper for HLD Architecture Diagram"""
    type: str = "diagram"
    response: HLDArchResponse
