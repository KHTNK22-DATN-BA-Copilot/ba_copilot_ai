# models/diagram.py
from pydantic import BaseModel

class DiagramResponse(BaseModel):
    type: str  # "class_diagram", "usecase_diagram", or "activity_diagram"
    detail: str  # Markdown content of the diagram

class DiagramOutput(BaseModel):
    type: str
    response: DiagramResponse
