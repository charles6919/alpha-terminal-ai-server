from dataclasses import dataclass


@dataclass(frozen=True)
class KakaoOAuthParams:
    client_id: str
    redirect_uri: str
    response_type: str = "code"
