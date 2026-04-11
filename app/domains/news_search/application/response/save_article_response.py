from datetime import datetime

from pydantic import BaseModel


class SaveArticleResponse(BaseModel):
    id: int
    saved_at: datetime
