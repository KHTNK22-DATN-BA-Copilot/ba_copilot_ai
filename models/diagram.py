# models/diagram.py
from pydantic import BaseModel

class DiagramResponse(BaseModel):
    figma_link: str
    editable: bool
    description: str

class DiagramOutput(BaseModel):
    type: str = "diagram"
    response: DiagramResponse
