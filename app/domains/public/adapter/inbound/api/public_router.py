from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domains.account.infrastructure.orm.account_orm import AccountORM
from app.domains.pipeline.adapter.outbound.persistence.analysis_log_repository_impl import AnalysisLogRepositoryImpl
from app.domains.pipeline.application.response.analysis_log_response import AnalysisLogResponse
from app.domains.pipeline.application.response.stock_summary_response import StockSummaryResponse
from app.domains.watchlist.infrastructure.orm.watchlist_item_orm import WatchlistItemORM
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/public", tags=["public"])

# 코스피 시총 1~5위 대표 종목
TOP_MARKET_CAP_SYMBOLS = ["005930", "000660", "373220", "207940", "005380"]
# 삼성전자, SK하이닉스, LG에너지솔루션, 삼성바이오로직스, 현대차
PUBLIC_SYMBOLS = TOP_MARKET_CAP_SYMBOLS  # 하위 호환
MAX_PUBLIC_SYMBOLS = 20


@router.get("/summaries", response_model=List[StockSummaryResponse])
async def get_public_summaries(
    symbols: str = ",".join(PUBLIC_SYMBOLS),
    db: Session = Depends(get_db),
):
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    log_repo = AnalysisLogRepositoryImpl(db)
    logs = log_repo.find_latest_by_symbols(symbol_list)
    return [
        StockSummaryResponse(
            symbol=log.symbol,
            name=log.name,
            summary=log.summary,
            tags=log.tags,
            sentiment=log.sentiment,
            sentiment_score=log.sentiment_score,
            confidence=log.confidence,
            source_type=log.source_type,
            url=log.url,
            analyzed_at=log.analyzed_at,
        )
        for log in logs
    ]


@router.get("/home-stats", response_model=List[AnalysisLogResponse])
async def get_public_home_stats(db: Session = Depends(get_db)):
    """시총 1~5위 대표 종목 + 시스템 전체 최신 5개 로그 기반 센티먼트 집계. 인증 불필요."""
    log_repo = AnalysisLogRepositoryImpl(db)
    seen: dict[str, AnalysisLogResponse] = {}

    # 1) 시총 1~5위 대표 종목 최신 로그
    for log in log_repo.find_latest_by_symbols(TOP_MARKET_CAP_SYMBOLS):
        seen[log.symbol] = log

    # 2) 시스템 전체 최신 5개 로그 (공개 관심종목 포함, 심볼 중복 제거)
    for log in log_repo.find_recent(limit=5, account_id=None):
        if log.symbol not in seen:
            seen[log.symbol] = log

    return list(seen.values())[:10]
