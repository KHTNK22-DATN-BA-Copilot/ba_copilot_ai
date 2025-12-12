# models/business_case.py
from pydantic import BaseModel

class BusinessCaseResponse(BaseModel):
    title: str
    content: str  # Complete markdown content with all sections

class BusinessCaseOutput(BaseModel):
    type: str = "business-case"
    response: BusinessCaseResponse
