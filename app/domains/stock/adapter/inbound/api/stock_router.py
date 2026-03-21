from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.domains.stock.adapter.outbound.persistence.in_memory_stock_repository import InMemoryStockRepository
from app.domains.stock.application.response.stock_search_response import StockSearchResult
from app.domains.stock.application.usecase.search_stock_usecase import SearchStockUseCase

router = APIRouter(prefix="/stocks", tags=["stocks"])

_repository = InMemoryStockRepository()
_usecase = SearchStockUseCase(_repository)


@router.get("/search", response_model=List[StockSearchResult])
async def search_stocks(q: str = Query(default=None)):
    if not q or len(q.strip()) < 1:
        raise HTTPException(status_code=400, detail="검색어는 1자 이상이어야 합니다.")
    try:
        results = _usecase.execute(q)
        return [StockSearchResult(symbol=s.symbol, name=s.name, market=s.market) for s in results]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
