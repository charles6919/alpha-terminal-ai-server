from typing import List, Tuple

from pydantic import BaseModel, Field


class HeatmapSummary(BaseModel):
    up: int = Field(ge=0)
    down: int = Field(ge=0)
    flat: int = Field(ge=0)


class HeatmapItem(BaseModel):
    symbol: str
    market: str
    series: List[Tuple[str, int]]
    summary: HeatmapSummary


class HeatmapErrorItem(BaseModel):
    symbol: str
    code: str
    message: str


class DailyReturnsHeatmapResponse(BaseModel):
    as_of: str | None = None
    weeks: int
    items: List[HeatmapItem]
    errors: List[HeatmapErrorItem] = Field(default_factory=list)
