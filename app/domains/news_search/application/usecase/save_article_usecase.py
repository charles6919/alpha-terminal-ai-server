import logging
from typing import Optional

from app.domains.news_search.application.request.save_article_request import SaveArticleRequest
from app.domains.news_search.application.response.save_article_response import SaveArticleResponse
from app.domains.news_search.application.usecase.article_content_fetcher_port import ArticleContentFetcherPort
from app.domains.news_search.application.usecase.article_content_store_port import ArticleContentStorePort
from app.domains.news_search.application.usecase.saved_article_repository_port import SavedArticleRepositoryPort
from app.domains.news_search.domain.entity.saved_article import SavedArticle

logger = logging.getLogger(__name__)


class SaveArticleUseCase:
    def __init__(
        self,
        repository: SavedArticleRepositoryPort,
        content_store: ArticleContentStorePort,
        content_fetcher: Optional[ArticleContentFetcherPort] = None,
    ):
        self._repository = repository
        self._content_store = content_store
        self._content_fetcher = content_fetcher

    def execute(self, request: SaveArticleRequest, account_id: int) -> SaveArticleResponse:
        existing = self._repository.find_by_link_and_account(request.link, account_id)
        if existing:
            raise ValueError("이미 저장된 기사입니다.")

        article = SavedArticle(
            title=request.title,
            link=request.link,
            source=request.source,
            snippet=request.snippet,
            published_at=request.published_at,
            account_id=account_id,
        )

        saved = self._repository.save(article)

        content = request.content
        if not content and request.link and self._content_fetcher:
            content = self._content_fetcher.fetch(request.link)

        raw_data = {
            "title": request.title,
            "link": request.link,
            "source": request.source,
            "snippet": request.snippet,
            "published_at": request.published_at,
            "content": content,
        }
        try:
            self._content_store.store(
                article_id=saved.id,
                account_id=account_id,
                raw_data=raw_data,
            )
        except Exception:
            logger.exception(
                "PostgreSQL content store failed; article id=%s remains in MySQL only",
                saved.id,
            )

        return SaveArticleResponse(
            id=saved.id,
            saved_at=saved.saved_at,
        )
