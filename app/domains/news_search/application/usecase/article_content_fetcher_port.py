from abc import ABC, abstractmethod
from typing import Optional


class ArticleContentFetcherPort(ABC):
    @abstractmethod
    def fetch(self, url: str) -> Optional[str]:
        """URL에서 기사 본문을 추출한다. 실패 시 None 반환."""
        ...
