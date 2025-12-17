# models/risk_register.py
from pydantic import BaseModel

class RiskRegisterResponse(BaseModel):
    """Response model for Risk Register document"""
    title: str
    executive_summary: str
    risk_identification: str
    risk_assessment: str
    mitigation_strategies: str
    contingency_plans: str
    detail: str

class RiskRegisterOutput(BaseModel):
    """Output wrapper for Risk Register"""
    type: str = "risk-register"
    response: RiskRegisterResponse
