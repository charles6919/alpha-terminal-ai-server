from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.domains.stock.domain.entity.stock import Stock


class StockRepositoryPort(ABC):

    @abstractmethod
    def search_by_name(self, keyword: str, limit: int = 20) -> List[Stock]:
        pass

    @abstractmethod
    def find_market_by_symbol(self, symbol: str) -> Optional[str]:
        """DB에 있으면 market 문자열, 없으면 None"""
        pass

    @abstractmethod
    def bulk_upsert(self, stocks: List[Stock]) -> int:
        """저장/업데이트 후 처리된 건수 반환"""
        pass

    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def update_market_bulk(self, market_map: Dict[str, str]) -> int:
        """종목코드 → 시장구분 딕셔너리로 market 컬럼 일괄 업데이트. 업데이트된 건수 반환"""
        pass
