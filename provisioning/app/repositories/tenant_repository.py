"""Acesso ao Banco Master. Responsabilidade exclusiva de persistência — nenhuma regra de
negócio aqui, conforme 00-AI-CONSTITUTION.md ("Repositories: Nunca validar regras.")."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.master import (
    AuditLog,
    Plan,
    Subscription,
    Tenant,
    TenantStatus,
    TenantUserIndex,
)


class TenantRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_document(self, document: str) -> Tenant | None:
        result = await self._session.execute(select(Tenant).where(Tenant.document == document))
        return result.scalar_one_or_none()

    async def get_by_id(self, tenant_id: uuid.UUID) -> Tenant | None:
        result = await self._session.execute(select(Tenant).where(Tenant.id == tenant_id))
        return result.scalar_one_or_none()

    async def create(self, tenant: Tenant) -> Tenant:
        self._session.add(tenant)
        await self._session.flush()
        return tenant

    async def update_status(self, tenant: Tenant, status: TenantStatus) -> Tenant:
        tenant.status = status.value
        await self._session.flush()
        return tenant

    async def get_active_plan(self) -> Plan | None:
        """Busca o Plano ativo a ser atribuído a cada novo tenant. Semeado por
        `scripts/seed_master.py` (já executado no boot do container, conforme
        `docker-entrypoint.sh`) — só existe 1 Plano nesta fase, mas a busca já é
        preparada para múltiplos (o primeiro ativo por ordem de criação)."""

        result = await self._session.execute(
            select(Plan).where(Plan.active.is_(True)).order_by(Plan.created_at).limit(1)
        )
        return result.scalar_one_or_none()

    async def create_subscription(self, subscription: Subscription) -> Subscription:
        self._session.add(subscription)
        await self._session.flush()
        return subscription

    async def get_user_index_by_email(self, email: str) -> TenantUserIndex | None:
        result = await self._session.execute(
            select(TenantUserIndex).where(TenantUserIndex.email == email)
        )
        return result.scalar_one_or_none()

    async def add_user_index(self, *, email: str, tenant_id: uuid.UUID) -> TenantUserIndex:
        """Registra a entrada de roteamento de login (e-mail → tenant) no Banco Master,
        conforme o fluxo obrigatório de 04-MULTI-TENANCY.md."""

        entry = TenantUserIndex(email=email, tenant_id=tenant_id)
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def add_audit_log(
        self,
        *,
        tenant_id: uuid.UUID | None,
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
