"""Auditoria genérica reutilizável por qualquer módulo de negócio, conforme
00-AI-CONSTITUTION.md ("Toda alteração deverá ser registrada. Nada poderá ser apagado
da auditoria.") e 05-BANCO-DE-DADOS.md.

Grava em `TenantAuditLog` (banco do tenant). Nenhum módulo deve montar essa tabela
manualmente — sempre through `record_audit_log`."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import TenantAuditLog


async def record_audit_log(
    session: AsyncSession,
    *,
    user_id: uuid.UUID | None,
    action: str,
    resource: str,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> TenantAuditLog:
    """Registra uma linha de auditoria na sessão do tenant já aberta. Não faz commit —
    a chamada deve ocorrer dentro da mesma transação da operação que está sendo
    auditada, para que ambas sejam persistidas (ou revertidas) juntas."""

    entry = TenantAuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        before=before,
        after=after,
    )
    session.add(entry)
    await session.flush()
    return entry
