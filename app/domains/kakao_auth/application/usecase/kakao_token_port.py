from abc import ABC, abstractmethod
from app.domains.kakao_auth.domain.entity.kakao_user import KakaoUser


class KakaoTokenPort(ABC):

    @abstractmethod
    def exchange_code_for_user(self, code: str) -> KakaoUser:
        pass
