from typing import List

from app.domains.stock.application.usecase.stock_repository_port import StockRepositoryPort
from app.domains.stock.domain.entity.stock import Stock


class SearchStockUseCase:

    def __init__(self, repository: StockRepositoryPort):
        self._repository = repository

    def execute(self, query: str) -> List[Stock]:
        if not query or len(query.strip()) < 1:
            raise ValueError("검색어는 1자 이상이어야 합니다.")
        return self._repository.search(query.strip())
