from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    query: str

class ChatSource(BaseModel):
    document_id: str
    filename: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource]
