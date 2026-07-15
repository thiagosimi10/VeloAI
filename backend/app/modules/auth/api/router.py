"""Controller do módulo de Autenticação. Responsabilidade: receber requisição, validar,
delegar ao Use Case e gerenciar cookies HttpOnly — nunca conter regra de negócio
(00-AI-CONSTITUTION.md). Nunca armazenar tokens em LocalStorage — sempre Cookies
HttpOnly (17-FRONTEND-ARCHITECTURE.md, 29-SECURITY.md)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from veloai_shared.exceptions import AuthenticationError
from veloai_shared.responses import SuccessResponse

from app.core.config import Settings, get_settings
from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import (
    ACCESS_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_COOKIE_NAME,
    CurrentUser,
    get_current_user,
    get_token_service,
)
from app.core.rate_limit import LoginRateLimiter, get_login_rate_limiter
from app.modules.auth.schemas.auth import ChangePasswordRequest, LoginRequest, MeResponse
from app.modules.auth.services.token_service import TokenService
from app.modules.auth.use_cases.change_password_use_case import ChangePasswordUseCase
from app.modules.auth.use_cases.login_use_case import LoginUseCase
from app.modules.auth.use_cases.logout_use_case import LogoutUseCase
from app.modules.auth.use_cases.me_use_case import MeUseCase
from app.modules.auth.use_cases.refresh_use_case import RefreshUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(
    response: Response, *, settings: Settings, access_token: str, refresh_token: str
) -> None:
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME, path="/")
    response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME, path="/")


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
    token_service: TokenService = Depends(get_token_service),
    rate_limiter: LoginRateLimiter = Depends(get_login_rate_limiter),
) -> SuccessResponse[MeResponse]:
    use_case = LoginUseCase(
        settings=settings,
        connection_manager=connection_manager,
        token_service=token_service,
        rate_limiter=rate_limiter,
    )
    result = await use_case.execute(
        email=payload.email,
        password=payload.password,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    _set_auth_cookies(
        response,
        settings=settings,
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )

    return SuccessResponse(
        message="Login realizado com sucesso.",
        data=MeResponse(
            id=result.user_id,
            email=result.email,
            first_name=result.first_name,
            last_name=result.last_name,
            role=result.role,
            permissions=result.permissions,
            must_change_password=result.must_change_password,
        ),
    )


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
    token_service: TokenService = Depends(get_token_service),
) -> SuccessResponse[dict[str, str]]:
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    if not refresh_token:
        raise AuthenticationError("Não autenticado.", code="NOT_AUTHENTICATED")

    use_case = RefreshUseCase(
        settings=settings,
        connection_manager=connection_manager,
        token_service=token_service,
    )
    result = await use_case.execute(refresh_token=refresh_token)

    _set_auth_cookies(
        response,
        settings=settings,
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )

    return SuccessResponse(message="Sessão renovada.", data={})


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
    token_service: TokenService = Depends(get_token_service),
) -> SuccessResponse[dict[str, str]]:
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    if refresh_token:
        use_case = LogoutUseCase(
            connection_manager=connection_manager, token_service=token_service
        )
        await use_case.execute(refresh_token=refresh_token)

    _clear_auth_cookies(response)

    return SuccessResponse(message="Logout realizado com sucesso.", data={})


@router.get("/me")
async def me(
    current_user: CurrentUser = Depends(get_current_user),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[MeResponse]:
    use_case = MeUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        user_id=current_user.user_id,
    )

    return SuccessResponse(
        message="Usuário autenticado.",
        data=MeResponse(
            id=result.id,
            email=result.email,
            first_name=result.first_name,
            last_name=result.last_name,
            role=result.role,
            permissions=result.permissions,
            must_change_password=result.must_change_password,
        ),
    )


@router.patch("/password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: CurrentUser = Depends(get_current_user),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[dict[str, str]]:
    use_case = ChangePasswordUseCase(connection_manager=connection_manager)
    await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        user_id=current_user.user_id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )

    return SuccessResponse(message="Senha atualizada com sucesso.", data={})
