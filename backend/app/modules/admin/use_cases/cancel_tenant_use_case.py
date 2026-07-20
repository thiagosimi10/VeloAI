"""Caso de uso: cancelar uma empresa a partir do Painel Administrativo. Nunca é uma
exclusão real — o banco de dados do tenant permanece intacto, apenas o status muda
para `CANCELED` (mesmo espírito de `billing/use_cases/cancel_subscription_use_case.py`
e de `11-FINANCEIRO.md`: "Nunca permitir exclusão... sempre uma ação reversível")."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import ConflictError, NotFoundError
from veloai_shared.schema.master import TenantStatus

from app.core.database import get_master_session
from app.modules.admin.repositories.admin_repository import AdminRepository


class CancelTenantUseCase:
    async def execute(self, *, tenant_id: uuid.UUID) -> None:
        async with get_master_session() as session:
            repository = AdminRepository(session)

            tenant = await repository.get_tenant_by_id(tenant_id)
            if tenant is None:
                raise NotFoundError("Empresa não encontrada.", code="TENANT_NOT_FOUND")

            if tenant.status == TenantStatus.CANCELED.value:
                raise ConflictError("Empresa já está cancelada.", code="TENANT_ALREADY_CANCELED")

            before_status = tenant.status
            await repository.update_tenant_status(tenant, TenantStatus.CANCELED)
            await repository.add_audit_log(
                tenant_id=tenant_id,
                action="ADMIN_TENANT_CANCELED",
                resource="tenants",
                before={"status": before_status},
                after={"status": TenantStatus.CANCELED.value},
            )
            await repository.commit()
