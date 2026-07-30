"""Controller do módulo Billing. Responsabilidade: receber requisição, validar
permissão via `require_permission` e delegar ao Use Case — nunca conter regra de
negócio (00-AI-CONSTITUTION.md). Nunca fica atrás de `require_active_subscription`
(ver `app/api/v1/router.py`) — um tenant com assinatura inativa precisa continuar
enxergando/cancelando a própria assinatura."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from veloai_shared.exceptions import AuthenticationError
from veloai_shared.responses import SuccessResponse

from app.core.asaas_client import AsaasClient, get_asaas_client
from app.core.config import Settings, get_settings
from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.modules.billing.permissions import BILLING_MANAGE, BILLING_VIEW
from app.modules.billing.schemas.billing import (
    CheckoutRequest,
    CheckoutResponse,
    PlanTierResponse,
    SubscriptionResponse,
)
from app.modules.billing.use_cases.cancel_subscription_use_case import CancelSubscriptionUseCase
from app.modules.billing.use_cases.create_checkout_use_case import CreateCheckoutUseCase
from app.modules.billing.use_cases.get_subscription_use_case import GetSubscriptionUseCase
from app.modules.billing.use_cases.handle_asaas_webhook_use_case import HandleAsaasWebhookUseCase
from app.modules.billing.use_cases.list_plan_tiers_use_case import ListPlanTiersUseCase

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/subscription")
async def get_subscription(
    current_user: CurrentUser = Depends(require_permission(BILLING_VIEW)),
) -> SuccessResponse[SubscriptionResponse]:
    use_case = GetSubscriptionUseCase()
    subscription = await use_case.execute(tenant_id=current_user.tenant_id)
    return SuccessResponse(message="Assinatura obtida com sucesso.", data=subscription)


@router.post("/cancel")
async def cancel_subscription(
    current_user: CurrentUser = Depends(require_permission(BILLING_MANAGE)),
) -> SuccessResponse[SubscriptionResponse]:
    use_case = CancelSubscriptionUseCase()
    subscription = await use_case.execute(tenant_id=current_user.tenant_id)
    return SuccessResponse(message="Assinatura cancelada com sucesso.", data=subscription)


@router.get("/plans")
async def list_plans(
    current_user: CurrentUser = Depends(require_permission(BILLING_VIEW)),
) -> SuccessResponse[list[PlanTierResponse]]:
    use_case = ListPlanTiersUseCase()
    tiers = await use_case.execute()
    return SuccessResponse(message="Planos obtidos com sucesso.", data=tiers)


@router.get("/public/plans")
async def list_public_plans() -> SuccessResponse[list[PlanTierResponse]]:
    """Mesmos dados de `/billing/plans`, mas sem autenticação — usado pelas páginas de
    marketing (`/`, `/comece-agora`) para nunca exibir um preço diferente do cobrado de
    verdade no checkout."""

    use_case = ListPlanTiersUseCase()
    tiers = await use_case.execute()
    return SuccessResponse(message="Planos obtidos com sucesso.", data=tiers)


@router.post("/checkout")
async def create_checkout(
    payload: CheckoutRequest,
    current_user: CurrentUser = Depends(require_permission(BILLING_MANAGE)),
    settings: Settings = Depends(get_settings),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
    asaas_client: AsaasClient = Depends(get_asaas_client),
) -> SuccessResponse[CheckoutResponse]:
    use_case = CreateCheckoutUseCase(
        settings=settings, connection_manager=connection_manager, asaas_client=asaas_client
    )
    checkout = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        user_id=current_user.user_id,
        cycle=payload.cycle,
    )
    return SuccessResponse(message="Checkout criado com sucesso.", data=checkout)


@router.post("/webhooks/asaas")
async def asaas_webhook(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> SuccessResponse[dict[str, str]]:
    """Recebido diretamente pela Asaas — nunca fica atrás de autenticação de usuário
    (`CurrentUser`). Autenticidade validada pelo header `asaas-access-token`, que deve
    bater com o `authToken` configurado ao criar o Webhook no painel Asaas."""

    token = request.headers.get("asaas-access-token")
    if not token or token != settings.asaas_webhook_token:
        raise AuthenticationError("Webhook não autorizado.", code="INVALID_WEBHOOK_TOKEN")

    payload = await request.json()
    use_case = HandleAsaasWebhookUseCase()
    await use_case.execute(payload)

    return SuccessResponse(message="Evento processado.", data={})
