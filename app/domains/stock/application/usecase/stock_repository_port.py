from abc import ABC, abstractmethod
from typing import List

from app.domains.stock.domain.entity.stock import Stock


class StockRepositoryPort(ABC):

    @abstractmethod
    def search(self, query: str) -> List[Stock]:
        """symbol 또는 name에 query가 포함된 종목을 반환한다."""
        pass
