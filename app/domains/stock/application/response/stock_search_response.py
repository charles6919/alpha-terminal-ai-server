from pydantic import BaseModel


class StockSearchResult(BaseModel):
    symbol: str
    name: str
    market: str
