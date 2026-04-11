import logging
from typing import Optional

import trafilatura

from app.domains.news_search.application.usecase.article_content_fetcher_port import ArticleContentFetcherPort

logger = logging.getLogger(__name__)


class ArticleContentFetcher(ArticleContentFetcherPort):
    def fetch(self, url: str) -> Optional[str]:
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return None
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
            )
            return text
        except Exception as e:
            logger.warning("[ArticleContentFetcher] 본문 추출 실패 url=%s err=%s", url, e)
            return None
