from typing import List

from app.domains.stock.adapter.outbound.external.finnhub_symbol_search_adapter import search_finnhub_us_stocks
from app.domains.stock.application.response.stock_response import StockResponse
from app.domains.stock.application.usecase.stock_repository_port import StockRepositoryPort

_MERGE_LIMIT = 20


class SearchStockUseCase:

    def __init__(self, repository: StockRepositoryPort, finnhub_api_key: str = ""):
        self._repository = repository
        self._finnhub_api_key = finnhub_api_key or ""

    def execute(self, keyword: str) -> List[StockResponse]:
        from_db = self._repository.search_by_name(keyword)
        out: List[StockResponse] = [
            StockResponse(symbol=s.symbol, name=s.name, market=s.market) for s in from_db
        ]
        seen = {r.symbol.upper() for r in out}

        if self._finnhub_api_key and len(out) < _MERGE_LIMIT:
            finnhub_rows = search_finnhub_us_stocks(
                keyword,
                self._finnhub_api_key,
                limit=_MERGE_LIMIT,
            )
            for row in finnhub_rows:
                if row.symbol.upper() in seen:
                    continue
                if len(out) >= _MERGE_LIMIT:
                    break
                out.append(row)
                seen.add(row.symbol.upper())

        return out
