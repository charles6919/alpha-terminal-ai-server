from abc import ABC, abstractmethod
from typing import List, Optional

from app.domains.news_search.domain.entity.saved_article import SavedArticle


class SavedArticleRepositoryPort(ABC):
    @abstractmethod
    def save(self, article: SavedArticle) -> SavedArticle:
        pass

    @abstractmethod
    def find_by_link_and_account(self, link: str, account_id: int) -> Optional[SavedArticle]:
        pass

    @abstractmethod
    def find_by_id(self, article_id: int) -> Optional[SavedArticle]:
        pass

    @abstractmethod
    def find_all_by_account(self, account_id: int) -> List[SavedArticle]:
        pass
