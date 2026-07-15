"""Acesso ao Banco Master. Responsabilidade exclusiva de persistência — nenhuma regra de
negócio aqui, conforme 00-AI-CONSTITUTION.md ("Repositories: Nunca validar regras.")."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.master import AuditLog, Tenant, TenantStatus, TenantUserIndex


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
