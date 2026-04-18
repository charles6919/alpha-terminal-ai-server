from abc import ABC, abstractmethod
from typing import List, Optional


class WatchlistSummaryPort(ABC):
    @abstractmethod
    def find_all(self, account_id: Optional[int] = None) -> List:
        """계정의 관심종목 목록 반환. symbol, name, market 속성을 가진 객체 리스트."""
        pass
