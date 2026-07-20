"""Caso de uso: editar os dados cadastrais (razão social / nome fantasia) de uma
empresa a partir do Painel Administrativo. Nunca altera `document`/`database_name` —
esses são definidos apenas no provisionamento."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import get_master_session
from app.modules.admin.repositories.admin_repository import AdminRepository


class UpdateTenantUseCase:
    async def execute(
        self, *, tenant_id: uuid.UUID, legal_name: str, trade_name: str | None
    ) -> None:
        async with get_master_session() as session:
            repository = AdminRepository(session)

            tenant = await repository.get_tenant_by_id(tenant_id)
            if tenant is None:
                raise NotFoundError("Empresa não encontrada.", code="TENANT_NOT_FOUND")

            before = {"legal_name": tenant.legal_name, "trade_name": tenant.trade_name}
            await repository.update_tenant(tenant, legal_name=legal_name, trade_name=trade_name)
            await repository.add_audit_log(
                tenant_id=tenant_id,
                action="ADMIN_TENANT_UPDATED",
                resource="tenants",
                before=before,
                after={"legal_name": legal_name, "trade_name": trade_name},
            )
            await repository.commit()
