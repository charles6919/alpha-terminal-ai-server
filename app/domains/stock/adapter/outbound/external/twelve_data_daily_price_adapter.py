"""Twelve Data - 미국장 일별 종가 조회."""

from __future__ import annotations

import logging
from typing import List, Tuple

import httpx

logger = logging.getLogger(__name__)

TWELVE_DATA_URL = "https://api.twelvedata.com/time_series"


def fetch_daily_closes_from_twelve_data(
    symbol: str,
    outputsize: int,
    api_key: str,
    exchange: str | None = None,
) -> tuple[list[tuple[str, float]] | None, str | None, str | None]:
    """
    반환: ([(YYYY-MM-DD, close)], error_code, error_message)
    """
    if not api_key:
        return None, "NO_PROVIDER_KEY", "Twelve Data API 키가 설정되지 않았습니다."

    ex = (exchange or "").strip().upper()
    params: dict[str, str] = {
        "symbol": symbol.upper(),
        "interval": "1day",
        "outputsize": str(outputsize),
        "apikey": api_key,
        "format": "JSON",
    }
    if ex:
        params["exchange"] = ex
    try:
        res = httpx.get(TWELVE_DATA_URL, params=params, timeout=20.0)
        res.raise_for_status()
        data = res.json()
    except httpx.HTTPStatusError as e:
        status = e.response.status_code if e.response is not None else "?"
        logger.warning("[TwelveDataDaily] HTTP %s symbol=%s", status, symbol)
        return None, "PROVIDER_HTTP_ERROR", "미국장 일별 시세 API 호출에 실패했습니다."
    except Exception as e:
        logger.warning("[TwelveDataDaily] 요청 실패 symbol=%s error=%s", symbol, type(e).__name__)
        return None, "PROVIDER_ERROR", "미국장 일별 시세 API 호출에 실패했습니다."

    if isinstance(data, dict) and data.get("status") == "error":
        message = str(data.get("message") or "미국장 일별 데이터를 가져오지 못했습니다.")
        code = str(data.get("code") or "NO_DATA")
        logger.warning("[TwelveDataDaily] API 오류 symbol=%s code=%s", symbol, code)
        return None, "PROVIDER_API_ERROR", message

    values = data.get("values") if isinstance(data, dict) else None
    if not isinstance(values, list):
        return None, "NO_DATA", "미국장 일별 데이터를 가져오지 못했습니다."

    out: List[Tuple[str, float]] = []
    for row in values:
        if not isinstance(row, dict):
            continue
        dt = str(row.get("datetime") or "").strip()
        close_s = str(row.get("close") or "").strip()
        if not dt or not close_s:
            continue
        day = dt.split(" ", 1)[0]
        try:
            close_v = float(close_s)
        except ValueError:
            continue
        out.append((day, close_v))

    if not out:
        return None, "NO_DATA", "미국장 일별 데이터를 가져오지 못했습니다."

    out.sort(key=lambda x: x[0])
    return out, None, None
