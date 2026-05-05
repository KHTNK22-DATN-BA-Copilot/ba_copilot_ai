from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Response:
    summary: str
    content: Any
    status_code: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "content": self.content,
            "status_code": self.status_code,
        }


def success_response(summary: str, content: Any) -> Dict[str, Any]:
    return Response(summary=summary, content=content, status_code=200).to_dict()


def error_response(summary: str, content: Any) -> Dict[str, Any]:
    return Response(summary=summary, content=content, status_code=500).to_dict()
