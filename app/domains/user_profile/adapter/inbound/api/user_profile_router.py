from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from app.domains.auth.adapter.outbound.in_memory.redis_session_adapter import RedisSessionAdapter
from app.domains.user_profile.adapter.outbound.persistence.user_profile_repository_impl import (
    UserProfileRepositoryImpl,
)
from app.domains.user_profile.application.request.save_clicked_card_request import SaveClickedCardRequest
from app.domains.user_profile.application.request.save_recently_viewed_request import SaveRecentlyViewedRequest
from app.domains.user_profile.application.request.update_investment_profile_request import UpdateInvestmentProfileRequest
from app.domains.user_profile.application.response.user_profile_response import (
    UserProfileResponse, SaveRecentlyViewedResponse, SaveClickedCardResponse, InvestmentProfileResponse,
)
from app.domains.user_profile.application.usecase.get_user_profile_usecase import GetUserProfileUseCase
from app.domains.user_profile.application.usecase.save_clicked_card_usecase import SaveClickedCardUseCase
from app.domains.user_profile.application.usecase.save_recently_viewed_usecase import SaveRecentlyViewedUseCase
from app.domains.watchlist.adapter.outbound.persistence.watchlist_repository_impl import WatchlistRepositoryImpl
from app.infrastructure.cache.redis_client import redis_client
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/users", tags=["user-profile"])

_session_adapter = RedisSessionAdapter(redis_client)


def _resolve_account_id(
    account_id_cookie: Optional[str],
    user_token: Optional[str],
) -> Optional[int]:
    if account_id_cookie:
        try:
            return int(account_id_cookie)
        except ValueError:
            pass
    if user_token:
        session = _session_adapter.find_by_token(user_token)
        if session:
            try:
                return int(session.user_id)
            except ValueError:
                pass
    return None


@router.get("/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    account_id: Optional[str] = Cookie(default=None),
    user_token: Optional[str] = Cookie(default=None),
):
    requester_id = _resolve_account_id(account_id, user_token)
    if requester_id is None:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    if requester_id != user_id:
        raise HTTPException(status_code=403, detail="본인 프로필만 조회할 수 있습니다.")

    user_profile_repo = UserProfileRepositoryImpl(db)
    watchlist_repo = WatchlistRepositoryImpl(db)
    usecase = GetUserProfileUseCase(
        repository=user_profile_repo,
        watchlist_port=watchlist_repo,
    )
    return usecase.execute(account_id=user_id)


@router.get("/{user_id}/investment-profile", response_model=InvestmentProfileResponse)
async def get_investment_profile(
    user_id: int,
    db: Session = Depends(get_db),
    account_id: Optional[str] = Cookie(default=None),
    user_token: Optional[str] = Cookie(default=None),
):
    requester_id = _resolve_account_id(account_id, user_token)
    if requester_id is None:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    if requester_id != user_id:
        raise HTTPException(status_code=403, detail="본인 프로필만 조회할 수 있습니다.")

    repo = UserProfileRepositoryImpl(db)
    profile = repo.find_by_account_id(user_id)
    if profile is None:
        return InvestmentProfileResponse()
    return InvestmentProfileResponse(
        investment_style=profile.investment_style,
        risk_tolerance=profile.risk_tolerance,
        preferred_sectors=profile.preferred_sectors,
        analysis_preference=profile.analysis_preference,
        keywords_of_interest=profile.keywords_of_interest,
    )


@router.patch("/{user_id}/investment-profile", response_model=InvestmentProfileResponse)
async def update_investment_profile(
    user_id: int,
    request: UpdateInvestmentProfileRequest,
    db: Session = Depends(get_db),
    account_id: Optional[str] = Cookie(default=None),
    user_token: Optional[str] = Cookie(default=None),
):
    requester_id = _resolve_account_id(account_id, user_token)
    if requester_id is None:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    if requester_id != user_id:
        raise HTTPException(status_code=403, detail="본인 프로필만 수정할 수 있습니다.")

    from app.domains.user_profile.domain.entity.user_profile import UserProfile
    repo = UserProfileRepositoryImpl(db)
    existing = repo.find_by_account_id(user_id) or UserProfile(account_id=user_id)
    existing.investment_style = request.investment_style
    existing.risk_tolerance = request.risk_tolerance
    existing.preferred_sectors = request.preferred_sectors
    existing.analysis_preference = request.analysis_preference
    existing.keywords_of_interest = request.keywords_of_interest
    saved = repo.save(existing)
    return InvestmentProfileResponse(
        investment_style=saved.investment_style,
        risk_tolerance=saved.risk_tolerance,
        preferred_sectors=saved.preferred_sectors,
        analysis_preference=saved.analysis_preference,
        keywords_of_interest=saved.keywords_of_interest,
    )


@router.post("/{user_id}/recently-viewed", response_model=SaveRecentlyViewedResponse)
async def save_recently_viewed(
    user_id: int,
    request: SaveRecentlyViewedRequest,
    db: Session = Depends(get_db),
    account_id: Optional[str] = Cookie(default=None),
    user_token: Optional[str] = Cookie(default=None),
):
    requester_id = _resolve_account_id(account_id, user_token)
    if requester_id is None:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    if requester_id != user_id:
        raise HTTPException(status_code=403, detail="본인 이력만 저장할 수 있습니다.")

    repo = UserProfileRepositoryImpl(db)
    usecase = SaveRecentlyViewedUseCase(repository=repo)
    return usecase.execute(account_id=user_id, request=request)


@router.post("/{user_id}/clicked-cards", response_model=SaveClickedCardResponse)
async def save_clicked_card(
    user_id: int,
    request: SaveClickedCardRequest,
    db: Session = Depends(get_db),
    account_id: Optional[str] = Cookie(default=None),
    user_token: Optional[str] = Cookie(default=None),
):
    requester_id = _resolve_account_id(account_id, user_token)
    if requester_id is None:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    if requester_id != user_id:
        raise HTTPException(status_code=403, detail="본인 이력만 저장할 수 있습니다.")

    repo = UserProfileRepositoryImpl(db)
    usecase = SaveClickedCardUseCase(repository=repo)
    return usecase.execute(account_id=user_id, request=request)
