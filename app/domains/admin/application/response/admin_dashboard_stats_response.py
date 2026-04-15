from typing import Optional

from pydantic import BaseModel


class RetentionPoint(BaseModel):
    day: int
    rate: float  # 0.0 ~ 1.0


class AdminDashboardStatsResponse(BaseModel):
    total_users: int
    new_users_today: int
    new_users_this_week: int
    retention: list[RetentionPoint]   # D-1 ~ D-14
    avg_dwell_time_seconds: Optional[float]  # None = 추적 데이터 없음
    ctr: Optional[float]                     # None = 추적 데이터 없음
