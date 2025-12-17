# models/lld_pseudo.py
from pydantic import BaseModel

class LLDPseudoResponse(BaseModel):
    """Response model for Pseudocode Document"""
    title: str
    algorithm_overview: str
    input_output: str
    pseudocode: str
    complexity_analysis: str
    edge_cases: str
    implementation_notes: str
    detail: str

class LLDPseudoOutput(BaseModel):
    """Output wrapper for Pseudocode"""
    type: str = "lld-pseudo"
    response: LLDPseudoResponse
