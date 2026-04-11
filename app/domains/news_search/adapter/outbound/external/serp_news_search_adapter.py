from typing import List, Tuple

from app.domains.news_search.application.usecase.news_search_port import NewsSearchPort
from app.domains.news_search.domain.entity.news_article import NewsArticle
from app.infrastructure.external.serp_client import SerpClient


class SerpNewsSearchAdapter(NewsSearchPort):
    def __init__(self, hl: str = "en", gl: str = "us") -> None:
        self._client = SerpClient()
        self._hl = hl
        self._gl = gl

    def search(self, keyword: str, page: int, page_size: int) -> Tuple[List[NewsArticle], int]:
        start = (page - 1) * page_size

        data = self._client.get({
            "engine": "google_news",
            "q": keyword,
            "hl": self._hl,
            "gl": self._gl,
            "start": start,
            "num": page_size,
        })

        news_results = data.get("news_results", [])
        total_count = data.get("search_information", {}).get("total_results", len(news_results))

        articles = [
            NewsArticle(
                title=item.get("title", ""),
                snippet=item.get("snippet", ""),
                source=item.get("source", {}).get("name", ""),
                published_at=item.get("date", None),
                link=item.get("link", None),
            )
            for item in news_results
        ]

        return articles, total_count
