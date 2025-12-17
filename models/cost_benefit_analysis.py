# models/cost_benefit_analysis.py
from pydantic import BaseModel

class CostBenefitAnalysisResponse(BaseModel):
    """Response model for Cost-Benefit Analysis document"""
    title: str
    executive_summary: str
    cost_analysis: str
    benefit_analysis: str
    roi_calculation: str
    npv_analysis: str
    payback_period: str
    detail: str

class CostBenefitAnalysisOutput(BaseModel):
    """Output wrapper for Cost-Benefit Analysis"""
    type: str = "cost-benefit-analysis"
    response: CostBenefitAnalysisResponse
