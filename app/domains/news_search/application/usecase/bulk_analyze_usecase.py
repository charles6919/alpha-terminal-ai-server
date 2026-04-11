import asyncio
import logging
from typing import Optional

from app.domains.news_search.application.request.analyze_article_request import AnalyzeArticleRequest
from app.domains.news_search.application.request.bulk_analyze_request import BulkAnalyzeRequest
from app.domains.news_search.application.response.bulk_analyze_response import BulkAnalyzeItem, BulkAnalyzeResponse
from app.domains.news_search.application.usecase.analyze_article_usecase import AnalyzeArticleUseCase
from app.domains.news_search.application.usecase.article_analysis_port import ArticleAnalysisPort
from app.domains.news_search.application.usecase.article_content_store_port import ArticleContentStorePort
from app.domains.news_search.application.usecase.news_search_port import NewsSearchPort
from app.domains.news_search.application.usecase.saved_article_repository_port import SavedArticleRepositoryPort
from app.domains.news_search.domain.entity.news_article import NewsArticle
from app.domains.news_search.domain.entity.saved_article import SavedArticle

logger = logging.getLogger(__name__)

_BULK_SYSTEM_ACCOUNT_ID = 0


class BulkAnalyzeUseCase:
    def __init__(
        self,
        news_search_port: NewsSearchPort,
        repository: SavedArticleRepositoryPort,
        content_store: ArticleContentStorePort,
        analysis_port: ArticleAnalysisPort,
    ):
        self._news_search_port = news_search_port
        self._repository = repository
        self._content_store = content_store
        self._analyze_usecase = AnalyzeArticleUseCase(repository, analysis_port, content_store)

    def _save_article(self, article: NewsArticle, account_id: int) -> Optional[int]:
        try:
            existing = self._repository.find_by_link_and_account(article.link, account_id)
            if existing:
                return existing.id

            saved = self._repository.save(SavedArticle(
                title=article.title,
                link=article.link,
                source=article.source,
                snippet=article.snippet,
                published_at=article.published_at,
                account_id=account_id,
            ))

            self._content_store.store(
                article_id=saved.id,
                account_id=account_id,
                raw_data={
                    "title": article.title,
                    "link": article.link,
                    "source": article.source,
                    "snippet": article.snippet,
                    "published_at": article.published_at,
                    "content": None,
                },
            )

            return saved.id
        except Exception as e:
            logger.warning(f"기사 저장 실패 [{article.title}]: {e}")
            return None

    async def _analyze(self, article_id: int, title: str) -> Optional[BulkAnalyzeItem]:
        try:
            analysis = await self._analyze_usecase.execute(AnalyzeArticleRequest(article_id=article_id))
            return BulkAnalyzeItem(
                article_id=article_id,
                title=title,
                sentiment=analysis.sentiment,
                sentiment_score=analysis.sentiment_score,
                keywords=analysis.keywords,
            )
        except Exception as e:
            logger.warning(f"기사 분석 건너뜀 [id={article_id}]: {e}")
            return None

    async def execute(self, request: BulkAnalyzeRequest, account_id: Optional[int] = None) -> BulkAnalyzeResponse:
        effective_account_id = account_id if account_id is not None else _BULK_SYSTEM_ACCOUNT_ID
        articles, _ = self._news_search_port.search(request.query, page=1, page_size=request.page_size)
        articles = articles[:request.page_size]

        # 1단계: 전체 저장 (순차 — DB 세션 충돌 방지)
        saved_pairs = []
        for article in articles:
            article_id = self._save_article(article, effective_account_id)
            if article_id is not None:
                saved_pairs.append((article_id, article.title))

        # 2단계: 전체 분석 (병렬 — OpenAI API 동시 호출)
        tasks = [self._analyze(article_id, title) for article_id, title in saved_pairs]
        items = await asyncio.gather(*tasks, return_exceptions=True)

        results = [item for item in items if isinstance(item, BulkAnalyzeItem)]

        return BulkAnalyzeResponse(
            query=request.query,
            total=len(results),
            results=results,
        )
