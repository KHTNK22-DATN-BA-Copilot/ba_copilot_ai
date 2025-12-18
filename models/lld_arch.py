# models/lld_arch.py
from pydantic import BaseModel

class LLDArchResponse(BaseModel):
    """Response model for Low-Level Design Architecture Diagram"""
    type: str
    detail: str

class LLDArchOutput(BaseModel):
    """Output wrapper for LLD Architecture Diagram"""
    type: str = "diagram"
    response: LLDArchResponse
