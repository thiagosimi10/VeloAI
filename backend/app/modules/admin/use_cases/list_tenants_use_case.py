"""Caso de uso: listar todos os Tenants (Painel Administrativo, Fase 18), com plano e
status de assinatura reais — dados já existentes desde a Fase 17, nunca fabricados
para esta tela."""

from __future__ import annotations

from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import get_master_session
from app.modules.admin.repositories.admin_repository import AdminRepository
from app.modules.admin.schemas.admin import TenantOverviewItem


@dataclass(frozen=True)
class ListTenantsResult:
    items: list[TenantOverviewItem]
    meta: PaginationMeta


class ListTenantsUseCase:
    async def execute(self, *, page: int, page_size: int) -> ListTenantsResult:
        async with get_master_session() as session:
            repository = AdminRepository(session)

            total = await repository.count_tenants()
            tenants = await repository.list_tenants(page=page, page_size=page_size)

            plan_ids = {tenant.plan_id for tenant in tenants if tenant.plan_id is not None}
            tenant_ids = {tenant.id for tenant in tenants}
            plans_by_id = await repository.get_plans_by_ids(plan_ids)
            subscriptions_by_tenant = await repository.get_subscriptions_by_tenant_ids(
                tenant_ids
            )

        items = [
            TenantOverviewItem(
                tenant_id=tenant.id,
                legal_name=tenant.legal_name,
                document=tenant.document,
                status=tenant.status,
                plan_name=(
                    plans_by_id[tenant.plan_id].name if tenant.plan_id in plans_by_id else None
                ),
                subscription_status=(
                    subscriptions_by_tenant[tenant.id].status
                    if tenant.id in subscriptions_by_tenant
                    else None
                ),
                trial_ends_at=(
                    subscriptions_by_tenant[tenant.id].trial_ends_at
                    if tenant.id in subscriptions_by_tenant
                    else None
                ),
            )
            for tenant in tenants
        ]

        pages = (total + page_size - 1) // page_size if total else 0
        return ListTenantsResult(
            items=items,
            meta=PaginationMeta(page=page, page_size=page_size, total=total, pages=pages),
        )
