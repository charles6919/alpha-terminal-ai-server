import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

_scheduler = AsyncIOScheduler()


async def _run_profile_update():
    from app.domains.user_profile.adapter.outbound.persistence.user_profile_repository_impl import (
        UserProfileRepositoryImpl,
    )
    from app.domains.user_profile.application.usecase.update_all_user_profiles_usecase import (
        UpdateAllUserProfilesUseCase,
    )
    from app.infrastructure.database.session import SessionLocal

    logger.info("[ProfileScheduler] 사용자 프로필 업데이트 배치 시작")
    db = SessionLocal()
    try:
        repo = UserProfileRepositoryImpl(db)
        usecase = UpdateAllUserProfilesUseCase(repo)
        updated_count = usecase.execute()
        logger.info("[ProfileScheduler] 사용자 프로필 업데이트 배치 완료 — %d명 갱신", updated_count)
    except Exception:
        logger.exception("[ProfileScheduler] 사용자 프로필 업데이트 배치 오류 — 다음 실행에 영향 없음")
    finally:
        db.close()


def start_profile_scheduler():
    _scheduler.add_job(
        _run_profile_update,
        trigger=CronTrigger(hour=0, minute=0, timezone="Asia/Seoul"),
        id="profile_update_midnight",
        name="00:00 KST 사용자 프로필 자동 업데이트",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("[ProfileScheduler] 프로필 업데이트 스케줄러 시작 — 매일 00:00 KST 실행")


def stop_profile_scheduler():
    if _scheduler.running:
        _scheduler.shutdown()
        logger.info("[ProfileScheduler] 프로필 업데이트 스케줄러 종료")
