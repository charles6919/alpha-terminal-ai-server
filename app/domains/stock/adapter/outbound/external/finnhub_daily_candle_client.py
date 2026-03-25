"""Finnhub 일봉 캔들 조회 (BL-BE-13)."""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Sequence, Tuple

import httpx

logger = logging.getLogger(__name__)

CANDLE_URL = "https://finnhub.io/api/v1/stock/candle"
_KR_NUMERIC = re.compile(r"^\d{6}$")


def resolve_finnhub_symbol(symbol: str, market: Optional[str]) -> Tuple[str, str]:
    """
    (finnhub_symbol, market_label) — 첫 시도용(하위호환).
    """
    s = symbol.strip()
    m = (market or "").upper()
    if m in ("KOSPI", "KOSDAQ", "KONEX") and _KR_NUMERIC.match(s):
        return f"KRX:{s}", m
    if m in ("NASDAQ", "NYSE"):
        return s.upper(), m
    if _KR_NUMERIC.match(s):
        return f"KRX:{s}", "KOSPI"
    return s.upper(), m or "US"


def finnhub_kr_symbol_candidates(symbol: str, market: Optional[str]) -> List[str]:
    """
    Finnhub 일봉에서 한국 종목은 KRX: 접두만으로는 no_data가 나오는 경우가 많아
    .KS / .KQ 등을 순차 시도한다.
    """
    s = symbol.strip()
    if not _KR_NUMERIC.match(s):
        return []
    m = (market or "").upper()
    out: List[str] = []
    if m == "KOSDAQ":
        out.extend([f"{s}.KQ", f"{s}.KS"])
    elif m == "KOSPI":
        out.extend([f"{s}.KS", f"{s}.KQ"])
    elif m == "KONEX":
        out.extend([f"KRX:{s}", f"{s}.KS"])
    else:
        out.extend([f"{s}.KS", f"{s}.KQ"])
    if f"KRX:{s}" not in out:
        out.append(f"KRX:{s}")
    # 중복 제거, 순서 유지
    seen = set()
    uniq: List[str] = []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def finnhub_symbol_candidates(symbol: str, market: Optional[str]) -> List[str]:
    """한국 6자리면 후보 목록, 미국 등은 단일 티커."""
    s = symbol.strip()
    if _KR_NUMERIC.match(s):
        return finnhub_kr_symbol_candidates(s, market)
    primary, _ = resolve_finnhub_symbol(s, market)
    return [primary]


def fetch_daily_closes(
    finnhub_symbol: str,
    from_ts: int,
    to_ts: int,
    token: str,
) -> Optional[Tuple[List[int], List[float]]]:
    """성공 시 (unix_seconds[], close[]), no_data/오류 시 None."""
    if not token:
        return None
    params = {
        "symbol": finnhub_symbol,
        "resolution": "D",
        "from": from_ts,
        "to": to_ts,
        "token": token,
    }
    try:
        r = httpx.get(CANDLE_URL, params=params, timeout=20.0)
        r.raise_for_status()
        data = r.json()
    except httpx.HTTPStatusError as e:
        status = e.response.status_code if e.response is not None else "?"
        if status == 403:
            logger.warning(
                "[FinnhubCandle] 403 Forbidden symbol=%s (현재 API 플랜에서 stock/candle 미지원 가능)",
                finnhub_symbol,
            )
        else:
            logger.warning("[FinnhubCandle] HTTP %s symbol=%s", status, finnhub_symbol)
        return None
    except Exception as e:
        logger.warning("[FinnhubCandle] 요청 실패 symbol=%s error=%s", finnhub_symbol, type(e).__name__)
        return None

    if not isinstance(data, dict):
        logger.warning("[FinnhubCandle] 비JSON 응답 %s", finnhub_symbol)
        return None
    status = data.get("s")
    if status == "no_data":
        logger.debug("[FinnhubCandle] no_data symbol=%s", finnhub_symbol)
        return None
    t = data.get("t")
    c = data.get("c")
    if not isinstance(t, list) or not isinstance(c, list) or len(t) != len(c) or not t:
        logger.warning("[FinnhubCandle] 예상치 못한 응답 symbol=%s keys=%s", finnhub_symbol, list(data.keys()))
        return None
    times = [int(x) for x in t]
    closes = [float(x) for x in c]
    return times, closes


def fetch_daily_closes_first_match(
    candidates: Sequence[str],
    from_ts: int,
    to_ts: int,
    token: str,
) -> Optional[Tuple[List[int], List[float]]]:
    for sym in candidates:
        got = fetch_daily_closes(sym, from_ts, to_ts, token)
        if got is not None:
            if sym != candidates[0]:
                logger.info("[FinnhubCandle] 대체 심볼 성공: %s (후보: %s)", sym, candidates)
            return got
    return None
