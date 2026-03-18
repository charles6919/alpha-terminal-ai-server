from app.domains.auth.application.usecase.session_store_port import SessionStorePort


class LogoutUseCase:

    def __init__(self, session_store: SessionStorePort):
        self._session_store = session_store

    def execute(self, token: str) -> None:
        self._session_store.delete(token)
