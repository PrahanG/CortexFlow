from pydantic import BaseModel
from typing import List

class SearchResultItem(BaseModel):
    id: str
    document_id: str
    filename: str
    content: str
    distance: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
