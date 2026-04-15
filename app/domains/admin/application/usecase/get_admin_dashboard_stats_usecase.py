"""관리자 대시보드 통계 UseCase.

현재 구현 가능한 지표:
    - total_users       : 전체 가입자 수
    - new_users_today   : 오늘 가입자 수
    - new_users_this_week: 이번 주 가입자 수
    - retention D-1~D-14: 가입 후 N일 뒤 재방문 비율
                          (활동 로그 테이블 없어 현재 0.0 반환, TODO)
    - avg_dwell_time    : 평균 체류 시간 (세션 추적 없어 None 반환, TODO)
    - ctr               : 카드 클릭률 (클릭/노출 추적 없어 None 반환, TODO)
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.domains.account.infrastructure.orm.account_orm import AccountORM
from app.domains.admin.application.response.admin_dashboard_stats_response import (
    AdminDashboardStatsResponse,
    RetentionPoint,
)


class GetAdminDashboardStatsUseCase:

    def __init__(self, db: Session):
        self._db = db

    def execute(self) -> AdminDashboardStatsResponse:
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())

        total_users = self._db.query(AccountORM).count()

        new_users_today = (
            self._db.query(AccountORM)
            .filter(AccountORM.created_at >= today_start)
            .count()
        )

        new_users_this_week = (
            self._db.query(AccountORM)
            .filter(AccountORM.created_at >= week_start)
            .count()
        )

        # Retention D-1 ~ D-14
        # TODO: 활동 로그 테이블(user_activity_log) 구축 후 실제 재방문 비율 계산
        retention = [RetentionPoint(day=d, rate=0.0) for d in range(1, 15)]

        return AdminDashboardStatsResponse(
            total_users=total_users,
            new_users_today=new_users_today,
            new_users_this_week=new_users_this_week,
            retention=retention,
            avg_dwell_time_seconds=None,  # TODO: 세션 체류 시간 추적 후 계산
            ctr=None,                     # TODO: 카드 클릭/노출 추적 후 계산
        )
