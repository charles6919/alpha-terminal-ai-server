import secrets
from app.domains.auth.application.request.login_request import LoginRequest
from app.domains.auth.application.response.login_response import LoginResponse
from app.domains.auth.application.usecase.session_store_port import SessionStorePort
from app.domains.auth.domain.entity.session import Session
from app.domains.auth.domain.value_object.user_role import UserRole


class LoginUseCase:
    SESSION_TTL_SECONDS = 3600  # 1 hour

    def __init__(self, session_store: SessionStorePort, auth_password: str):
        self._session_store = session_store
        self._auth_password = auth_password

    def execute(self, request: LoginRequest) -> LoginResponse:
        if request.password != self._auth_password:
            raise PermissionError("Invalid password")

        token = secrets.token_hex(32)
        role = UserRole.ADMIN if request.user_id == "admin" else UserRole.USER
        session = Session(
            token=token,
            user_id=request.user_id,
            role=role,
            ttl_seconds=self.SESSION_TTL_SECONDS,
        )
        self._session_store.save(session)

        return LoginResponse(
            token=token,
            user_id=session.user_id,
            role=session.role.value,
            ttl_seconds=session.ttl_seconds,
        )
