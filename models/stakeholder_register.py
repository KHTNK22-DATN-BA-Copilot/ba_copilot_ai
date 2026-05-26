from typing import List, Optional, TypedDict

from .chat_context_message import ChatContextMessage


class StakeholderRegisterState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[List[ChatContextMessage]]
