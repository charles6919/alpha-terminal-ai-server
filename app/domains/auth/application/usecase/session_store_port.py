from abc import ABC, abstractmethod
from typing import Optional
from app.domains.auth.domain.entity.session import Session


class SessionStorePort(ABC):

    @abstractmethod
    def save(self, session: Session) -> None:
        pass

    @abstractmethod
    def find_by_token(self, token: str) -> Optional[Session]:
        pass

    @abstractmethod
    def delete(self, token: str) -> None:
        pass
