"""data.go.kr 금융위원회_주식시세정보 - 한국장 일별 종가 조회."""

from __future__ import annotations

import logging
from typing import List, Tuple

import httpx

logger = logging.getLogger(__name__)

DATA_GO_KR_URL = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"


def _as_list(value: object) -> list[dict]:
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def fetch_daily_closes_from_data_go_kr(
    symbol: str,
    begin_date: str,
    end_date: str,
    service_key: str,
    num_rows: int = 120,
) -> tuple[list[tuple[str, float]] | None, str | None, str | None]:
    """
    반환: ([(YYYY-MM-DD, close)], error_code, error_message)
    """
    if not service_key:
        return None, "NO_PROVIDER_KEY", "data.go.kr 서비스키가 설정되지 않았습니다."

    base_params = {
        "serviceKey": service_key,
        "resultType": "json",
        "numOfRows": str(num_rows),
        "beginBasDt": begin_date,
        "endBasDt": end_date,
        "likeSrtnCd": symbol,
    }

    rows: list[dict] = []
    page_no = 1
    max_pages = 50

    while page_no <= max_pages:
        params = {**base_params, "pageNo": str(page_no)}
        try:
            res = httpx.get(DATA_GO_KR_URL, params=params, timeout=20.0)
            res.raise_for_status()
            data = res.json()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response is not None else "?"
            logger.warning("[DataGoKrDaily] HTTP %s symbol=%s page=%s", status, symbol, page_no)
            return None, "PROVIDER_HTTP_ERROR", "한국장 일별 시세 API 호출에 실패했습니다."
        except Exception as e:
            logger.warning("[DataGoKrDaily] 요청 실패 symbol=%s page=%s error=%s", symbol, page_no, type(e).__name__)
            return None, "PROVIDER_ERROR", "한국장 일별 시세 API 호출에 실패했습니다."

        try:
            response = (data or {}).get("response") or {}
            header = response.get("header") or {}
            result_code = str(header.get("resultCode") or "").strip()
            if result_code and result_code != "00":
                message = str(header.get("resultMsg") or "한국장 일별 시세 API 오류")
                logger.warning("[DataGoKrDaily] API 오류 symbol=%s code=%s", symbol, result_code)
                return None, "PROVIDER_API_ERROR", message

            body = response.get("body") or {}
            items = body.get("items") or {}
            page_rows = _as_list(items.get("item"))
        except Exception:
            page_rows = []

        if not page_rows:
            break
        rows.extend(page_rows)
        if len(page_rows) < num_rows:
            break
        page_no += 1

    by_day: dict[str, float] = {}
    for row in rows:
        raw_symbol = str(row.get("srtnCd") or "").strip()
        if raw_symbol.zfill(6) != symbol.zfill(6):
            continue
        bas_dt = str(row.get("basDt") or "").strip()
        close_s = str(row.get("clpr") or "").replace(",", "").strip()
        if len(bas_dt) != 8 or not close_s:
            continue
        try:
            close_v = float(close_s)
        except ValueError:
            continue
        day_iso = f"{bas_dt[:4]}-{bas_dt[4:6]}-{bas_dt[6:8]}"
        by_day[day_iso] = close_v

    if not by_day:
        return None, "NO_DATA", "한국장 일봉 데이터를 가져오지 못했습니다."

    out = sorted(by_day.items(), key=lambda x: x[0])
    return out, None, None
