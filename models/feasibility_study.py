# models/feasibility_study.py
from pydantic import BaseModel

class FeasibilityStudyResponse(BaseModel):
    """Response model for Feasibility Study document"""
    title: str
    executive_summary: str
    technical_feasibility: str
    operational_feasibility: str
    economic_feasibility: str
    schedule_feasibility: str
    legal_feasibility: str
    detail: str

class FeasibilityStudyOutput(BaseModel):
    """Output wrapper for Feasibility Study"""
    type: str = "feasibility-study"
    response: FeasibilityStudyResponse
