"""Caso de uso: iniciar o pagamento de um ciclo do plano VeloAI Professional via
Checkout hospedado da Asaas. Nunca muda o status da Assinatura aqui — só o webhook
(`handle_asaas_webhook_use_case.py`), disparado pela própria Asaas após a confirmação
real do pagamento, faz isso (ver `docs/31-BILLING.md`)."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from veloai_shared.exceptions import ValidationError
from veloai_shared.schema.tenant import Company

from app.core.asaas_client import AsaasClient
from app.core.config import Settings
from app.core.database import TenantConnectionManager, get_master_session
from app.modules.auth.repositories.user_repository import TenantUserRepository
from app.modules.billing.pricing import get_plan_tier
from app.modules.billing.repositories.subscription_repository import SubscriptionRepository
from app.modules.billing.schemas.billing import CheckoutResponse


class CreateCheckoutUseCase:
    def __init__(
        self,
        *,
        settings: Settings,
        connection_manager: TenantConnectionManager,
        asaas_client: AsaasClient,
    ) -> None:
        self._settings = settings
        self._connections = connection_manager
        self._asaas = asaas_client

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, user_id: uuid.UUID, cycle: str
    ) -> CheckoutResponse:
        tier = get_plan_tier(cycle)
        if tier is None:
            raise ValidationError("Ciclo de cobrança inválido.", code="INVALID_BILLING_CYCLE")

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            company = (await session.execute(select(Company))).scalars().first()
            user = await TenantUserRepository(session).get_by_id(user_id)
            assert company is not None  # toda empresa provisionada tem uma Company
            assert user is not None  # o próprio usuário autenticado da requisição

        base_url = self._settings.frontend_base_url
        data = await self._asaas.create_checkout(
            {
                "billingTypes": ["PIX", "CREDIT_CARD"],
                "chargeTypes": ["RECURRENT"],
                "items": [
                    {
                        # A Asaas limita `items[].name` a 30 caracteres — "VeloAI — {label}"
                        # cabe com folga para os 3 ciclos, "VeloAI Professional — ..." não.
                        "name": f"VeloAI — {tier.label}",
                        "description": "Assinatura do sistema de gestão VeloAI.",
                        "imageBase64": self._asaas.placeholder_item_image(),
                        "value": float(tier.total_price),
                        "quantity": 1,
                    }
                ],
                "customerData": {
                    "name": company.legal_name,
                    "cpfCnpj": company.document,
                    "email": user.email,
                },
                "subscription": {
                    "cycle": tier.cycle,
                    "nextDueDate": date.today().isoformat(),
                },
                "callback": {
                    "successUrl": f"{base_url}/billing?checkout=success",
                    "cancelUrl": f"{base_url}/billing?checkout=cancel",
                    "expiredUrl": f"{base_url}/billing?checkout=expired",
                },
                "externalReference": str(tenant_id),
            }
        )

        async with get_master_session() as master_session:
            subscription_repository = SubscriptionRepository(master_session)
            subscription = await subscription_repository.get_by_tenant_id(tenant_id)
            if subscription is not None:
                subscription.asaas_checkout_id = data["id"]
                await subscription_repository.commit()

        return CheckoutResponse(checkout_url=data["link"])
