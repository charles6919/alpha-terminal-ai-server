from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ArticleContentStorePort(ABC):
    @abstractmethod
    def store(self, article_id: int, account_id: int, raw_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_content(self, article_id: int) -> Optional[str]:
        """저장된 기사 본문(raw_data.content) 반환. 없으면 None."""
        pass
