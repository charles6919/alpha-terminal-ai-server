import datetime
import logging
import re
from hashlib import sha256
from typing import List

import httpx

from app.domains.stock_collector.application.usecase.collector_port import CollectorPort
from app.domains.stock_collector.domain.entity.raw_article import RawArticle
from app.infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)

_KR_CODE = re.compile(r"^\d{6}$")


class FinnhubCollectorAdapter(CollectorPort):
    API_URL = "https://finnhub.io/api/v1/company-news"

    def collect(self, symbol: str) -> List[RawArticle]:
        if _KR_CODE.match(symbol):
            return []

        settings = get_settings()
        today = datetime.date.today()
        from_date = (today - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
        to_date = today.strftime("%Y-%m-%d")

        params = {
            "symbol": symbol.upper(),
            "from": from_date,
            "to": to_date,
            "token": settings.finnhub_api_key,
        }

        try:
            response = httpx.get(self.API_URL, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            logger.warning("[FinnhubCollector] 요청 실패: %s", e)
            return []

        if not isinstance(data, list):
            logger.warning("[FinnhubCollector] 예상치 못한 응답: %s", data)
            return []

        now = datetime.datetime.now().isoformat()
        articles = []

        for item in data[:10]:
            url = item.get("url", "")
            title = item.get("headline", "")
            snippet = item.get("summary", "")
            ts = item.get("datetime", 0)
            published_at = (
                datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else ""
            )
            content = f"{title}{snippet}".encode()

            articles.append(
                RawArticle(
                    source_type="NEWS",
                    source_name="FINNHUB",
                    source_doc_id=sha256(url.encode()).hexdigest()[:20],
                    url=url,
                    title=title,
                    body_text=snippet,
                    published_at=published_at,
                    collected_at=now,
                    symbol=symbol,
                    lang="en",
                    content_hash=f"sha256:{sha256(content).hexdigest()}",
                    collector_version="collector-v1.0.0",
                    status="COLLECTED",
                    author=item.get("source", ""),
                    meta={"source": item.get("source", "")},
                )
            )

        return articles
