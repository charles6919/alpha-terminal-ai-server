from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class SavedArticleItemResponse(BaseModel):
    id: int
    title: str
    link: str
    source: str
    snippet: Optional[str]
    published_at: Optional[str]
    saved_at: datetime
    has_content: bool  # whether content exists in PostgreSQL


class SavedArticleListResponse(BaseModel):
    items: List[SavedArticleItemResponse]
    total: int
