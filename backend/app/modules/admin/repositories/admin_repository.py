"""Acesso ao Banco Master para o módulo Admin (Painel Administrativo, Fase 18).
Responsabilidade exclusiva de persistência — nenhuma regra de negócio aqui, conforme
00-AI-CONSTITUTION.md ("Repositories: Nunca validar regras."). Opera na sessão do
Banco Master (`get_master_session()`), mesmo padrão de `billing/repositories/
subscription_repository.py` — `Tenant`/`Plan`/`Subscription`/`AuditLog`/`PlatformAdmin`
vivem lá, nunca no banco de um tenant."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.master import (
    AuditLog,
    Plan,
    PlatformAdmin,
    Subscription,
    SubscriptionStatus,
    Tenant,
    TenantStatus,
)


class AdminRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_platform_admin_by_email(self, email: str) -> PlatformAdmin | None:
        result = await self._session.execute(
            select(PlatformAdmin).where(PlatformAdmin.email == email)
        )
        return result.scalar_one_or_none()

    async def get_platform_admin_by_id(self, admin_id: uuid.UUID) -> PlatformAdmin | None:
        return await self._session.get(PlatformAdmin, admin_id)

    async def update_password(self, admin: PlatformAdmin, password_hash: str) -> PlatformAdmin:
        admin.password_hash = password_hash
        admin.force_password_change = False
        await self._session.flush()
        return admin

    async def get_tenant_by_id(self, tenant_id: uuid.UUID) -> Tenant | None:
        return await self._session.get(Tenant, tenant_id)

    async def update_tenant(
        self, tenant: Tenant, *, legal_name: str, trade_name: str | None
    ) -> Tenant:
        tenant.legal_name = legal_name
        tenant.trade_name = trade_name
        await self._session.flush()
        return tenant

    async def update_tenant_status(self, tenant: Tenant, status: TenantStatus) -> Tenant:
        tenant.status = status.value
        await self._session.flush()
        return tenant

    async def add_audit_log(
        self,
        *,
        tenant_id: uuid.UUID | None,
        action: str,
        resource: str,
        before: dict[str, object] | None = None,
        after: dict[str, object] | None = None,
    ) -> AuditLog:
        entry = AuditLog(tenant_id=tenant_id, action=action, resource=resource, before=before, after=after)
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def count_tenants(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(Tenant))
        return result.scalar_one()

    async def list_tenants(self, *, page: int, page_size: int) -> list[Tenant]:
        result = await self._session.execute(
            select(Tenant)
            .order_by(Tenant.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all())

    async def get_plans_by_ids(self, plan_ids: set[uuid.UUID]) -> dict[uuid.UUID, Plan]:
        if not plan_ids:
            return {}
        result = await self._session.execute(select(Plan).where(Plan.id.in_(plan_ids)))
        return {plan.id: plan for plan in result.scalars().all()}

    async def get_subscriptions_by_tenant_ids(
        self, tenant_ids: set[uuid.UUID]
    ) -> dict[uuid.UUID, Subscription]:
        if not tenant_ids:
            return {}
        result = await self._session.execute(
            select(Subscription).where(Subscription.tenant_id.in_(tenant_ids))
        )
        return {subscription.tenant_id: subscription for subscription in result.scalars().all()}

    async def get_subscription_status_counts(self) -> dict[str, int]:
        result = await self._session.execute(
            select(Subscription.status, func.count()).group_by(Subscription.status)
        )
        return dict(result.all())

    async def get_estimated_mrr(self) -> Decimal:
        result = await self._session.execute(
            select(func.coalesce(func.sum(Plan.price), 0))
            .select_from(Subscription)
            .join(Plan, Plan.id == Subscription.plan_id)
            .where(Subscription.status == SubscriptionStatus.ACTIVE.value)
        )
        return result.scalar_one()

    async def count_audit_logs(self, tenant_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(AuditLog).where(AuditLog.tenant_id == tenant_id)
        )
        return result.scalar_one()

    async def list_audit_logs(
        self, tenant_id: uuid.UUID, *, page: int, page_size: int
    ) -> list[AuditLog]:
        result = await self._session.execute(
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all())

    async def commit(self) -> None:
        await self._session.commit()
