"""Caso de uso: log de auditoria de um tenant, para o Painel Administrativo (Fase 18,
"Logs"). Reaproveita `AuditLog` do Banco Master — já escrito de verdade pelo
Provisioning (ciclo de vida do tenant) e pelo módulo `billing/` (cancelamento de
assinatura) desde a Fase 17. Nenhuma tabela nova."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from veloai_shared.responses import PaginationMeta

from app.core.database import get_master_session
from app.modules.admin.repositories.admin_repository import AdminRepository
from app.modules.admin.schemas.admin import AuditLogEntryResponse


@dataclass(frozen=True)
class ListTenantAuditLogResult:
    items: list[AuditLogEntryResponse]
    meta: PaginationMeta


class ListTenantAuditLogUseCase:
    async def execute(
        self, *, tenant_id: uuid.UUID, page: int, page_size: int
    ) -> ListTenantAuditLogResult:
        async with get_master_session() as session:
            repository = AdminRepository(session)

            total = await repository.count_audit_logs(tenant_id)
            entries = await repository.list_audit_logs(tenant_id, page=page, page_size=page_size)

        items = [AuditLogEntryResponse.model_validate(entry) for entry in entries]
        pages = (total + page_size - 1) // page_size if total else 0
        return ListTenantAuditLogResult(
            items=items,
            meta=PaginationMeta(page=page, page_size=page_size, total=total, pages=pages),
        )
