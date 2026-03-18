from app.domains.kakao_auth.application.response.kakao_access_token_response import KakaoAccessTokenResponse
from app.domains.kakao_auth.application.usecase.request_kakao_access_token_port import RequestKakaoAccessTokenPort


class RequestKakaoAccessTokenUseCase:

    def __init__(self, port: RequestKakaoAccessTokenPort):
        self._port = port

    def execute(self, code: str) -> KakaoAccessTokenResponse:
        if not code:
            raise ValueError("Authorization code is required")
        token = self._port.request(code)
        return KakaoAccessTokenResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_in=token.expires_in,
            refresh_token=token.refresh_token,
            refresh_token_expires_in=token.refresh_token_expires_in,
            scope=token.scope,
        )
