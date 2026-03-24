import datetime
import logging
import re
from hashlib import sha256
from html import unescape
from typing import List
from urllib.parse import quote

import httpx

from app.domains.stock_collector.application.usecase.collector_port import CollectorPort
from app.domains.stock_collector.domain.entity.raw_article import RawArticle

logger = logging.getLogger(__name__)

_KR_CODE = re.compile(r"^\d{6}$")
_TITLE_RE = re.compile(r'"title":"([^"]{12,150})"')
_URL_RE = re.compile(r'href="(https://n\.news\.naver\.com[^"]+)"')
_TAG_RE = re.compile(r"<[^>]+>")

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

SYMBOL_TO_NAME = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "035420": "네이버",
    "035720": "카카오",
    "373220": "LG에너지솔루션",
    "005380": "현대자동차",
    "000270": "기아",
    "051910": "LG화학",
    "006400": "삼성SDI",
    "068270": "셀트리온",
    "060250": "NHN KCP",
    "234340": "헥토파이낸셜",
}


def _clean(text: str) -> str:
    return unescape(_TAG_RE.sub("", text)).strip()


class NaverNewsCollectorAdapter(CollectorPort):
    BASE_URL = "https://search.naver.com/search.naver"

    def collect(self, symbol: str) -> List[RawArticle]:
        if not _KR_CODE.match(symbol):
            return []

        keyword = SYMBOL_TO_NAME.get(symbol, symbol)
        url = f"{self.BASE_URL}?where=news&query={quote(keyword)}&sm=tab_jum"

        try:
            response = httpx.get(url, headers=_HEADERS, timeout=10.0, follow_redirects=True)
            response.raise_for_status()
            html = response.text
        except httpx.HTTPError as e:
            logger.warning("[NaverNewsCollector] 요청 실패: %s", e)
            return []

        titles = [_clean(t) for t in _TITLE_RE.findall(html) if len(_clean(t)) > 5]
        urls = list(dict.fromkeys(_URL_RE.findall(html)))

        now = datetime.datetime.now().isoformat()
        articles = []

        for title, article_url in list(zip(titles, urls))[:10]:
            content = title.encode()
            articles.append(
                RawArticle(
                    source_type="NEWS",
                    source_name="NAVER_NEWS",
                    source_doc_id=sha256(article_url.encode()).hexdigest()[:20],
                    url=article_url,
                    title=title,
                    body_text="",
                    published_at="",
                    collected_at=now,
                    symbol=symbol,
                    lang="ko",
                    content_hash=f"sha256:{sha256(content).hexdigest()}",
                    collector_version="collector-v1.0.0",
                    status="COLLECTED",
                    author="네이버뉴스",
                    meta={"keyword": keyword},
                )
            )

        return articles
