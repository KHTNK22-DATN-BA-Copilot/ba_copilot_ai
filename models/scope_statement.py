# models/scope_statement.py
from pydantic import BaseModel

class ScopeStatementResponse(BaseModel):
    title: str
    content: str  # Complete markdown content with all sections

class ScopeStatementOutput(BaseModel):
    type: str = "scope-statement"
    response: ScopeStatementResponse
