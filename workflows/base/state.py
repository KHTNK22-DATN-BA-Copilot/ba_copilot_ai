from typing import TypedDict, Optional, List


class BaseDocumentState(TypedDict):
    user_message: str
    response: dict
    content_id: Optional[str]
    extracted_text: Optional[str]
    chat_context: Optional[str]
    document_format: Optional[str]
    project_id: Optional[int]
    document_constraint: Optional[List[str]]
