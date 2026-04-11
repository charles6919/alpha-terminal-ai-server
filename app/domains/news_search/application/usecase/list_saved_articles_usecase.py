from typing import List

from app.domains.news_search.application.response.saved_article_item_response import SavedArticleItemResponse, SavedArticleListResponse
from app.domains.news_search.application.usecase.article_content_store_port import ArticleContentStorePort
from app.domains.news_search.application.usecase.saved_article_repository_port import SavedArticleRepositoryPort


class ListSavedArticlesUseCase:
    def __init__(self, repository: SavedArticleRepositoryPort, content_store: ArticleContentStorePort):
        self._repository = repository
        self._content_store = content_store

    def execute(self, account_id: int) -> SavedArticleListResponse:
        articles = self._repository.find_all_by_account(account_id)
        items = []
        for a in articles:
            content = self._content_store.get_content(a.id)
            items.append(SavedArticleItemResponse(
                id=a.id,
                title=a.title,
                link=a.link,
                source=a.source,
                snippet=a.snippet,
                published_at=a.published_at,
                saved_at=a.saved_at,
                has_content=bool(content),
            ))
        return SavedArticleListResponse(items=items, total=len(items))
