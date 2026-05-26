from typing import TypedDict


class ChatContextMessage(TypedDict):
    role: str
    content: str