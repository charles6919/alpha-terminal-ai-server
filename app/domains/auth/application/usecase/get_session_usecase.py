from typing import Optional
from app.domains.auth.application.response.session_response import SessionResponse
from app.domains.auth.application.usecase.session_store_port import SessionStorePort


class GetSessionUseCase:

    def __init__(self, session_store: SessionStorePort):
        self._session_store = session_store

    def execute(self, token: str) -> Optional[SessionResponse]:
        session = self._session_store.find_by_token(token)
        if session is None:
            return None
        return SessionResponse(
            token=session.token,
            user_id=session.user_id,
            role=session.role.value,
        )
