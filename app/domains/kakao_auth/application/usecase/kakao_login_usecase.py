import secrets
from app.domains.auth.application.usecase.session_store_port import SessionStorePort
from app.domains.auth.domain.entity.session import Session
from app.domains.auth.domain.value_object.user_role import UserRole
from app.domains.kakao_auth.application.response.kakao_login_response import KakaoLoginResponse
from app.domains.kakao_auth.application.usecase.kakao_token_port import KakaoTokenPort

SESSION_TTL_SECONDS = 3600


class KakaoLoginUseCase:

    def __init__(self, kakao_token_port: KakaoTokenPort, session_store: SessionStorePort):
        self._kakao_token_port = kakao_token_port
        self._session_store = session_store

    def execute(self, code: str) -> KakaoLoginResponse:
        kakao_user = self._kakao_token_port.exchange_code_for_user(code)

        token = secrets.token_hex(32)
        session = Session(
            token=token,
            user_id=kakao_user.kakao_id,
            role=UserRole.USER,
            ttl_seconds=SESSION_TTL_SECONDS,
        )
        self._session_store.save(session)

        return KakaoLoginResponse(
            token=token,
            user_id=kakao_user.kakao_id,
            nickname=kakao_user.nickname,
            role=UserRole.USER.value,
            ttl_seconds=SESSION_TTL_SECONDS,
        )
