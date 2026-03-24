import logging
import re
from html import unescape
from typing import List, Tuple
from urllib.parse import quote

import httpx

from app.domains.news_search.application.usecase.news_search_port import NewsSearchPort
from app.domains.news_search.domain.entity.news_article import NewsArticle

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}
_TITLE_RE = re.compile(r'"title":"([^"]{12,150})"')
_URL_RE = re.compile(r'href="(https://n\.news\.naver\.com[^"]+)"')
_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text: str) -> str:
    return unescape(_TAG_RE.sub("", text)).strip()


class NaverNewsSearchAdapter(NewsSearchPort):
    BASE_URL = "https://search.naver.com/search.naver"

    def search(self, keyword: str, page: int, page_size: int) -> Tuple[List[NewsArticle], int]:
        params = {"where": "news", "query": keyword, "sm": "tab_jum"}
        url = f"{self.BASE_URL}?where=news&query={quote(keyword)}&sm=tab_jum"

        response = httpx.get(url, headers=_HEADERS, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        html = response.text

        titles = [_clean(t) for t in _TITLE_RE.findall(html) if len(_clean(t)) > 5]
        urls = list(dict.fromkeys(_URL_RE.findall(html)))  # 중복 제거, 순서 유지

        articles = [
            NewsArticle(
                title=title,
                snippet="",
                source="네이버뉴스",
                published_at=None,
                link=link,
            )
            for title, link in zip(titles, urls)
        ]

        total = len(articles)
        start = (page - 1) * page_size
        paged = articles[start: start + page_size]

        return paged, total
