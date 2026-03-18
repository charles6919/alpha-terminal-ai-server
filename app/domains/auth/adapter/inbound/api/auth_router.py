from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from app.domains.auth.application.request.login_request import LoginRequest
from app.domains.auth.application.response.login_response import LoginResponse
from app.domains.auth.application.response.session_response import SessionResponse
from app.domains.auth.application.usecase.get_session_usecase import GetSessionUseCase
from app.domains.auth.application.usecase.login_usecase import LoginUseCase
from app.domains.auth.application.usecase.logout_usecase import LogoutUseCase
from app.domains.auth.adapter.outbound.in_memory.redis_session_adapter import RedisSessionAdapter
from app.infrastructure.cache.redis_client import redis_client
from app.infrastructure.config.settings import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])

_settings = get_settings()
_session_adapter = RedisSessionAdapter(redis_client)
_login_usecase = LoginUseCase(_session_adapter, _settings.auth_password)
_logout_usecase = LogoutUseCase(_session_adapter)
_get_session_usecase = GetSessionUseCase(_session_adapter)


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    try:
        return _login_usecase.execute(request)
    except PermissionError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    token = _extract_token(authorization)
    _logout_usecase.execute(token)
    return {"message": "Logged out successfully"}


@router.get("/session", response_model=SessionResponse)
async def get_session(authorization: Optional[str] = Header(None)):
    token = _extract_token(authorization)
    session = _get_session_usecase.execute(token)
    if session is None:
        raise HTTPException(status_code=401, detail="Session not found or expired")
    return session


def _extract_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return authorization.removeprefix("Bearer ").strip()
