from dataclasses import dataclass


@dataclass
class Stock:
    symbol: str
    name: str
    market: str  # KOSPI | KOSDAQ | NASDAQ | NYSE
