import datetime
import logging
from typing import List, Tuple

import httpx

from app.domains.news_search.application.usecase.news_search_port import NewsSearchPort
from app.domains.news_search.domain.entity.news_article import NewsArticle
from app.infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)


class FinnhubNewsSearchAdapter(NewsSearchPort):
    API_URL = "https://finnhub.io/api/v1/company-news"

    def search(self, keyword: str, page: int, page_size: int) -> Tuple[List[NewsArticle], int]:
        settings = get_settings()
        today = datetime.date.today()
        from_date = (today - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
        to_date = today.strftime("%Y-%m-%d")

        params = {
            "symbol": keyword.upper(),
            "from": from_date,
            "to": to_date,
            "token": settings.finnhub_api_key,
        }

        response = httpx.get(self.API_URL, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            logger.warning("Finnhub unexpected response: %s", data)
            return [], 0

        articles = [
            NewsArticle(
                title=item.get("headline", ""),
                snippet=item.get("summary", ""),
                source=item.get("source", ""),
                published_at=datetime.datetime.fromtimestamp(item["datetime"]).strftime("%Y-%m-%d")
                if item.get("datetime")
                else None,
                link=item.get("url", None),
            )
            for item in data
        ]

        total = len(articles)
        start = (page - 1) * page_size
        paged = articles[start: start + page_size]

        return paged, total
