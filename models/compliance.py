# models/compliance.py
from pydantic import BaseModel

class ComplianceResponse(BaseModel):
    """Response model for Compliance document"""
    title: str
    executive_summary: str
    regulatory_requirements: str
    legal_requirements: str
    compliance_status: str
    recommendations: str
    detail: str

class ComplianceOutput(BaseModel):
    """Output wrapper for Compliance"""
    type: str = "compliance"
    response: ComplianceResponse
