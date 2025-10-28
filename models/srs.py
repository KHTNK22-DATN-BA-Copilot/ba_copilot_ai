# models/srs.py
from pydantic import BaseModel

class SRSResponse(BaseModel):
    title: str
    functional_requirements: str
    non_functional_requirements: str
    detail: str  # Markdown format

class SRSOutput(BaseModel):
    type: str = "srs"
    response: SRSResponse
