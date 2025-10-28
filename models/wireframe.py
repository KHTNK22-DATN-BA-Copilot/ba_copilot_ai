# models/wireframe.py
from pydantic import BaseModel

class WireframeResponse(BaseModel):
    figma_link: str
    editable: bool
    description: str

class WireframeOutput(BaseModel):
    type: str = "wireframe"
    response: WireframeResponse