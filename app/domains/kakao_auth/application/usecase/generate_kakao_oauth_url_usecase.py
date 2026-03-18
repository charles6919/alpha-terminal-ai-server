from app.domains.kakao_auth.application.usecase.generate_kakao_oauth_url_port import GenerateKakaoOAuthUrlPort
from app.domains.kakao_auth.application.response.kakao_oauth_url_response import KakaoOAuthUrlResponse


class GenerateKakaoOAuthUrlUseCase:

    def __init__(self, kakao_oauth_port: GenerateKakaoOAuthUrlPort):
        self._kakao_oauth_port = kakao_oauth_port

    def execute(self) -> KakaoOAuthUrlResponse:
        url = self._kakao_oauth_port.generate()
        return KakaoOAuthUrlResponse(authorization_url=url)
