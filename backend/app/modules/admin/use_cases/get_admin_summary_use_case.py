"""Caso de uso: resumo executivo do Painel Administrativo (Fase 18) — contagens reais
por status de assinatura + MRR estimado (soma do preço do Plano de cada assinatura
ACTIVE). Sem Churn/ARR/LTV/CAC nesta fase — exigiriam histórico de eventos que não
existe ainda."""

from __future__ import annotations

from veloai_shared.schema.master import SubscriptionStatus

from app.core.database import get_master_session
from app.modules.admin.repositories.admin_repository import AdminRepository
from app.modules.admin.schemas.admin import AdminSummaryResponse


class GetAdminSummaryUseCase:
    async def execute(self) -> AdminSummaryResponse:
        async with get_master_session() as session:
            repository = AdminRepository(session)

            total_tenants = await repository.count_tenants()
            counts_by_status = await repository.get_subscription_status_counts()
            estimated_mrr = await repository.get_estimated_mrr()

        return AdminSummaryResponse(
            total_tenants=total_tenants,
            trial_count=counts_by_status.get(SubscriptionStatus.TRIAL.value, 0),
            active_count=counts_by_status.get(SubscriptionStatus.ACTIVE.value, 0),
            pending_payment_count=counts_by_status.get(
                SubscriptionStatus.PENDING_PAYMENT.value, 0
            ),
            overdue_count=counts_by_status.get(SubscriptionStatus.OVERDUE.value, 0),
            suspended_count=counts_by_status.get(SubscriptionStatus.SUSPENDED.value, 0),
            canceled_count=counts_by_status.get(SubscriptionStatus.CANCELED.value, 0),
            expired_count=counts_by_status.get(SubscriptionStatus.EXPIRED.value, 0),
            estimated_mrr=estimated_mrr,
        )
