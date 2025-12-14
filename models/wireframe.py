# models/wireframe.py
from pydantic import BaseModel

class WireframeResponse(BaseModel):
    figma_link: str
    editable: bool
    description: str

class WireframeOutput(BaseModel):
    type: str = "wireframe"
    response: WireframeResponse

# Wireframe HTML CSS
# wrap to help validation, serialization (.json()), typehint (static type checking, IDE)
class WireframeHTMLCSSResponse(BaseModel):
    content: str

class WireframeHTMLCSSOutput(BaseModel):
    type: str = "wireframe_html_css"
    response: WireframeHTMLCSSResponse
