from typing import Dict, List, Optional, TypedDict

from .chat_context_message import ChatContextMessage


class UIUXWireframeState(TypedDict):
    message: str
    content_id: Optional[str]
    storage_paths: Optional[List[str]]
    response: Optional[Dict]
    extracted_text: Optional[str]
    chat_context: Optional[List[ChatContextMessage]]
