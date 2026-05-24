from typing import TypedDict, Optional, List


class BaseDocumentState(TypedDict):
    user_message: str
    response: dict

    content_id: Optional[str]

    storage_paths: Optional[List]
    extracted_text: Optional[str]
    chat_context: Optional[str]

    document_format: Optional[str]
