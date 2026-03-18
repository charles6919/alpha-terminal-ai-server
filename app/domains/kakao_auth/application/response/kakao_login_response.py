from pydantic import BaseModel


class KakaoLoginResponse(BaseModel):
    token: str
    user_id: str
    nickname: str
    role: str
    ttl_seconds: int
