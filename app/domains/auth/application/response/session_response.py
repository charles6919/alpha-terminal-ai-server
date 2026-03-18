from pydantic import BaseModel


class SessionResponse(BaseModel):
    token: str
    user_id: str
    role: str
