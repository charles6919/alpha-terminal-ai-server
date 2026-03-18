from abc import ABC, abstractmethod
from app.domains.kakao_auth.domain.entity.kakao_access_token import KakaoAccessToken


class RequestKakaoAccessTokenPort(ABC):

    @abstractmethod
    def request(self, code: str) -> KakaoAccessToken:
        pass
