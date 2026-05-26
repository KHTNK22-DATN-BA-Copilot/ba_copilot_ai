# models/product_roadmap.py
from typing import Dict, List, Optional, TypedDict

from pydantic import BaseModel

from .chat_context_message import ChatContextMessage

class ProductRoadmapResponse(BaseModel):
    type: str  # "product-roadmap"
    detail: str  # Mermaid gantt chart markdown

class ProductRoadmapOutput(BaseModel):
    type: str = "diagram"
    response: ProductRoadmapResponse


class ProductRoadmapState(TypedDict):
    user_message: Optional[str]
    response: Optional[dict]
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[List[ChatContextMessage]]
    raw_diagram: Optional[str]
    validation_result: Optional[dict]
    retry_count: int
