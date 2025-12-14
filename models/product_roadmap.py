# models/product_roadmap.py
from pydantic import BaseModel

class ProductRoadmapResponse(BaseModel):
    type: str  # "product-roadmap"
    detail: str  # Mermaid gantt chart markdown

class ProductRoadmapOutput(BaseModel):
    type: str = "diagram"
    response: ProductRoadmapResponse
