from pydantic import BaseModel


class KakaoOAuthUrlResponse(BaseModel):
    authorization_url: str
