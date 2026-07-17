"""Acesso ao Banco Master para o módulo Billing. Responsabilidade exclusiva de
persistência — nenhuma regra de negócio aqui, conforme 00-AI-CONSTITUTION.md
("Repositories: Nunca validar regras."). Diferente de todo outro `repository` do
Backend, este opera na sessão do Banco Master (`get_master_session()`), nunca na
sessão de um tenant específico — Billing é o primeiro módulo do Backend com dados que
vivem no Master, não no banco do tenant."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.master import AuditLog, Plan, Subscription, SubscriptionStatus


class SubscriptionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_tenant_id(self, tenant_id: uuid.UUID) -> Subscription | None:
        result = await self._session.execute(
            select(Subscription).where(Subscription.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_plan(self, plan_id: uuid.UUID) -> Plan | None:
        return await self._session.get(Plan, plan_id)

    async def update_status(
        self, subscription: Subscription, status: SubscriptionStatus
    ) -> Subscription:
        subscription.status = status.value
        await self._session.flush()
        return subscription

    async def add_audit_log(
        self,
        *,
        tenant_id: uuid.UUID,
        action: str,
        resource: str,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            tenant_id=tenant_id,
            action=action,
            resource=resource,
            before=before,
            after=after,
        )
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def commit(self) -> None:
        await self._session.commit()
