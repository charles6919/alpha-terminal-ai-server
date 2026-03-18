from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.domains.auth.adapter.outbound.in_memory.redis_session_adapter import RedisSessionAdapter
from app.domains.kakao_auth.adapter.outbound.external.kakao_oauth_adapter import KakaoOAuthAdapter
from app.domains.kakao_auth.adapter.outbound.external.kakao_token_adapter import KakaoTokenAdapter
from app.domains.kakao_auth.application.response.kakao_access_token_response import KakaoAccessTokenResponse
from app.domains.kakao_auth.application.response.kakao_login_response import KakaoLoginResponse
from app.domains.kakao_auth.application.usecase.generate_kakao_oauth_url_usecase import GenerateKakaoOAuthUrlUseCase
from app.domains.kakao_auth.application.usecase.kakao_login_usecase import KakaoLoginUseCase
from app.domains.kakao_auth.application.usecase.request_kakao_access_token_usecase import RequestKakaoAccessTokenUseCase
from app.infrastructure.cache.redis_client import redis_client
from app.infrastructure.config.settings import get_settings

router = APIRouter(prefix="/kakao-authentication", tags=["kakao-authentication"])

_settings = get_settings()

_kakao_oauth_adapter = KakaoOAuthAdapter(
    client_id=_settings.kakao_client_id,
    redirect_uri=_settings.kakao_redirect_uri,
)
_generate_url_usecase = GenerateKakaoOAuthUrlUseCase(_kakao_oauth_adapter)

_kakao_token_adapter = KakaoTokenAdapter(
    client_id=_settings.kakao_client_id,
    redirect_uri=_settings.kakao_redirect_uri,
)
_session_store = RedisSessionAdapter(redis_client)
_kakao_login_usecase = KakaoLoginUseCase(_kakao_token_adapter, _session_store)
_request_access_token_usecase = RequestKakaoAccessTokenUseCase(_kakao_token_adapter)


@router.get("/request-oauth-link")
async def request_oauth_link():
    response = _generate_url_usecase.execute()
    return RedirectResponse(url=response.authorization_url)


@router.get("/request-access-token-after-redirection", response_model=KakaoAccessTokenResponse)
async def request_access_token_after_redirection(code: str = None, error: str = None, error_description: str = None):
    if error:
        raise HTTPException(status_code=400, detail=f"Kakao OAuth error: {error} - {error_description}")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing")
    try:
        return _request_access_token_usecase.execute(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/redirection", response_model=KakaoLoginResponse)
async def kakao_redirection(code: str = None, error: str = None, error_description: str = None):
    if error:
        raise HTTPException(status_code=400, detail=f"Kakao OAuth error: {error} - {error_description}")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing")
    try:
        return _kakao_login_usecase.execute(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
