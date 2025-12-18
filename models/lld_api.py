# models/lld_api.py
from pydantic import BaseModel

class LLDAPIResponse(BaseModel):
    """Response model for API Specifications Document"""
    title: str
    api_overview: str
    authentication: str
    endpoints: str
    data_models: str
    error_handling: str
    rate_limiting: str
    versioning: str
    detail: str

class LLDAPIOutput(BaseModel):
    """Output wrapper for API Specifications"""
    type: str = "lld-api"
    response: LLDAPIResponse
