"""Finnhub 심볼 검색 — 미국 등 DB에 없는 종목 보강."""

from __future__ import annotations

import logging
import re
from typing import List, Tuple

import httpx

from app.domains.stock.application.response.stock_response import StockResponse

logger = logging.getLogger(__name__)

SEARCH_URL = "https://finnhub.io/api/v1/search"
# 미국 티커: BRK.B, BF.A 등
_US_TICKER = re.compile(r"^[A-Z]{1,5}(\.[A-Z])?$")


def _parse_finnhub_row_symbol(raw: str) -> Tuple[str, str]:
    """
    displaySymbol / symbol 파싱.
    반환: (티커, MIC 또는 접두 힌트). 예: "US:AAPL" -> ("AAPL", "US")
    """
    s = (raw or "").strip()
    if not s:
        return "", ""
    if ":" in s:
        prefix, rest = s.split(":", 1)
        return rest.strip().upper(), prefix.strip().upper()
    return s.upper(), ""


def _market_from_exchange(exchange: str, currency: str | None) -> str:
    ex = (exchange or "").upper()
    if ex == "US":
        return "NASDAQ"
    if ex in ("XNAS", "XNCM", "XNMS"):
        return "NASDAQ"
    if ex in ("ARCX", "BATS"):
        return "NYSE"
    if ex == "XNYS":
        return "NYSE"
    if "NASDAQ" in ex or "NMS" in ex or "NGM" in ex:
        return "NASDAQ"
    if "NYSE" in ex or "NEW YORK" in ex:
        return "NYSE"
    if "AMEX" in ex or "ARCA" in ex or "BATS" in ex:
        return "NYSE"
    if (currency or "").upper() == "USD":
        return "NASDAQ"
    return ""


def _guess_us_market_from_ticker(ticker: str) -> str:
    """Finnhub /search 가 exchange를 안 줄 때(흔함) 티커 형태로 US 주식으로 간주."""
    if not ticker or (ticker.isdigit() and len(ticker) == 6):
        return ""
    if _US_TICKER.match(ticker):
        return "NASDAQ"
    return ""


def search_finnhub_us_stocks(query: str, token: str, limit: int = 15) -> List[StockResponse]:
    """Finnhub /search 로 미국 주식 위주 검색. 키 없거나 실패 시 []."""
    q = (query or "").strip()
    if not q or not token:
        return []
    try:
        r = httpx.get(SEARCH_URL, params={"q": q, "token": token}, timeout=15.0)
        r.raise_for_status()
        data = r.json()
    except httpx.HTTPStatusError as e:
        status = e.response.status_code if e.response is not None else "?"
        logger.warning("[FinnhubSearch] HTTP %s query=%s", status, q)
        return []
    except Exception as e:
        logger.warning("[FinnhubSearch] 요청 실패 query=%s error=%s", q, type(e).__name__)
        return []

    if isinstance(data, dict) and data.get("error"):
        logger.warning("[FinnhubSearch] API 오류: %s", data.get("error"))
        return []

    raw = data.get("result")
    if not isinstance(raw, list):
        logger.debug("[FinnhubSearch] result 비리스트: %s", type(raw))
        return []

    out: List[StockResponse] = []
    seen: set[str] = set()
    for item in raw:
        if len(out) >= limit:
            break
        if not isinstance(item, dict):
            continue
        typ_l = (item.get("type") or "").lower()
        if any(x in typ_l for x in ("etf", "mutual fund", "bond", "crypto", "currency", "index")):
            continue

        raw_sym = (item.get("displaySymbol") or item.get("symbol") or "").strip()
        if not raw_sym:
            continue

        ticker, mic_hint = _parse_finnhub_row_symbol(raw_sym)
        if not ticker:
            continue

        # 한국 6자리 숫자 티커는 DB 검색에 맡김
        if ticker.isdigit() and len(ticker) == 6:
            continue
        # Finnhub 한국 접두
        if mic_hint in ("KRX", "KSE", "KOE", "KQ"):
            continue

        exchange = str(item.get("exchange") or "")
        currency = item.get("currency")
        cur_s = currency if isinstance(currency, str) else None

        market = _market_from_exchange(exchange, cur_s)
        if not market and mic_hint:
            market = _market_from_exchange(mic_hint, cur_s)
        if not market:
            market = _guess_us_market_from_ticker(ticker)
        if not market:
            continue

        desc = (item.get("description") or ticker).strip() or ticker
        key = ticker.upper()
        if key in seen:
            continue
        seen.add(key)
        out.append(StockResponse(symbol=key, name=desc, market=market))
    return out
