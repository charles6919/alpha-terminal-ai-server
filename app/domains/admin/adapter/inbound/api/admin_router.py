from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domains.admin.application.response.admin_dashboard_stats_response import AdminDashboardStatsResponse
from app.domains.admin.application.usecase.get_admin_dashboard_stats_usecase import GetAdminDashboardStatsUseCase
from app.infrastructure.auth.require_admin import require_admin
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard/stats", response_model=AdminDashboardStatsResponse)
async def get_dashboard_stats(
    account_id: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """관리자 전용 대시보드 통계 조회. NORMAL 역할 접근 시 403."""
    usecase = GetAdminDashboardStatsUseCase(db)
    return usecase.execute()
