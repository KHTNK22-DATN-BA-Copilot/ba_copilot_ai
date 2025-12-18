# models/lld_db.py
from pydantic import BaseModel

class LLDDBResponse(BaseModel):
    """Response model for Database Schema ERD"""
    type: str
    detail: str

class LLDDBOutput(BaseModel):
    """Output wrapper for Database Schema"""
    type: str = "database-schema"
    response: LLDDBResponse
