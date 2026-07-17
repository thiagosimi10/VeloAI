"""Controller do módulo Admin (Painel Administrativo, Fase 18). Responsabilidade:
receber requisição, delegar ao Use Case e gerenciar o cookie de sessão do Platform
Admin — nunca conter regra de negócio (00-AI-CONSTITUTION.md). Cookie HttpOnly próprio
(`admin_access_token`), nunca reaproveita o cookie/secret de sessão de tenant."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Request, Response
from veloai_shared.responses import SuccessResponse

from app.core.config import Settings, get_settings
from app.core.rate_limit import LoginRateLimiter, get_login_rate_limiter
from app.modules.admin.dependencies import (
    ADMIN_ACCESS_TOKEN_COOKIE_NAME,
    CurrentPlatformAdmin,
    get_current_platform_admin,
    get_platform_admin_token_service,
)
from app.modules.admin.schemas.admin import (
    AdminLoginRequest,
    AdminSummaryResponse,
    AuditLogEntryResponse,
    ChangeAdminPasswordRequest,
    PlatformAdminResponse,
    TenantOverviewItem,
)
from app.modules.admin.services.platform_admin_token_service import PlatformAdminTokenService
from app.modules.admin.use_cases.change_platform_admin_password_use_case import (
    ChangePlatformAdminPasswordUseCase,
)
from app.modules.admin.use_cases.get_admin_summary_use_case import GetAdminSummaryUseCase
from app.modules.admin.use_cases.list_tenant_audit_log_use_case import (
    ListTenantAuditLogUseCase,
)
from app.modules.admin.use_cases.list_tenants_use_case import ListTenantsUseCase
from app.modules.admin.use_cases.login_platform_admin_use_case import (
    LoginPlatformAdminUseCase,
)
from app.modules.admin.use_cases.me_platform_admin_use_case import MePlatformAdminUseCase

router = APIRouter(prefix="/admin", tags=["admin"])


def _set_admin_cookie(response: Response, *, settings: Settings, token: str) -> None:
    response.set_cookie(
        key=ADMIN_ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.platform_admin_token_expire_minutes * 60,
        path="/",
    )


@router.post("/auth/login")
async def login(
    payload: AdminLoginRequest,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
    token_service: PlatformAdminTokenService = Depends(get_platform_admin_token_service),
    rate_limiter: LoginRateLimiter = Depends(get_login_rate_limiter),
) -> SuccessResponse[PlatformAdminResponse]:
    use_case = LoginPlatformAdminUseCase(token_service=token_service, rate_limiter=rate_limiter)
    result = await use_case.execute(
        email=payload.email,
        password=payload.password,
        ip=request.client.host if request.client else None,
    )

    _set_admin_cookie(response, settings=settings, token=result.token)

    return SuccessResponse(
        message="Login realizado com sucesso.",
        data=PlatformAdminResponse(
            id=result.admin_id,
            email=result.email,
            first_name=result.first_name,
            last_name=result.last_name,
            must_change_password=result.must_change_password,
        ),
    )


@router.post("/auth/logout")
async def logout(response: Response) -> SuccessResponse[dict[str, str]]:
    response.delete_cookie(ADMIN_ACCESS_TOKEN_COOKIE_NAME, path="/")
    return SuccessResponse(message="Logout realizado com sucesso.", data={})


@router.get("/auth/me")
async def me(
    current_admin: CurrentPlatformAdmin = Depends(get_current_platform_admin),
) -> SuccessResponse[PlatformAdminResponse]:
    use_case = MePlatformAdminUseCase()
    profile = await use_case.execute(admin_id=current_admin.admin_id)

    return SuccessResponse(
        message="Operador autenticado.",
        data=PlatformAdminResponse(
            id=profile.id,
            email=profile.email,
            first_name=profile.first_name,
            last_name=profile.last_name,
            must_change_password=profile.must_change_password,
        ),
    )


@router.patch("/auth/password")
async def change_password(
    payload: ChangeAdminPasswordRequest,
    current_admin: CurrentPlatformAdmin = Depends(get_current_platform_admin),
) -> SuccessResponse[dict[str, str]]:
    use_case = ChangePlatformAdminPasswordUseCase()
    await use_case.execute(
        admin_id=current_admin.admin_id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )

    return SuccessResponse(message="Senha atualizada com sucesso.", data={})


@router.get("/tenants")
async def list_tenants(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _current_admin: CurrentPlatformAdmin = Depends(get_current_platform_admin),
) -> SuccessResponse[list[TenantOverviewItem]]:
    use_case = ListTenantsUseCase()
    result = await use_case.execute(page=page, page_size=page_size)

    return SuccessResponse(
        message="Tenants obtidos com sucesso.", data=result.items, meta=result.meta
    )


@router.get("/tenants/{tenant_id}/audit-log")
async def list_tenant_audit_log(
    tenant_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _current_admin: CurrentPlatformAdmin = Depends(get_current_platform_admin),
) -> SuccessResponse[list[AuditLogEntryResponse]]:
    use_case = ListTenantAuditLogUseCase()
    result = await use_case.execute(tenant_id=tenant_id, page=page, page_size=page_size)

    return SuccessResponse(
        message="Log de auditoria obtido com sucesso.", data=result.items, meta=result.meta
    )


@router.get("/summary")
async def get_summary(
    _current_admin: CurrentPlatformAdmin = Depends(get_current_platform_admin),
) -> SuccessResponse[AdminSummaryResponse]:
    use_case = GetAdminSummaryUseCase()
    summary = await use_case.execute()

    return SuccessResponse(message="Resumo obtido com sucesso.", data=summary)
