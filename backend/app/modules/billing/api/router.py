"""Controller do módulo Billing. Responsabilidade: receber requisição, validar
permissão via `require_permission` e delegar ao Use Case — nunca conter regra de
negócio (00-AI-CONSTITUTION.md). Nunca fica atrás de `require_active_subscription`
(ver `app/api/v1/router.py`) — um tenant com assinatura inativa precisa continuar
enxergando/cancelando a própria assinatura."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from veloai_shared.responses import SuccessResponse

from app.core.dependencies import CurrentUser, require_permission
from app.modules.billing.permissions import BILLING_MANAGE, BILLING_VIEW
from app.modules.billing.schemas.billing import SubscriptionResponse
from app.modules.billing.use_cases.cancel_subscription_use_case import CancelSubscriptionUseCase
from app.modules.billing.use_cases.get_subscription_use_case import GetSubscriptionUseCase

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
