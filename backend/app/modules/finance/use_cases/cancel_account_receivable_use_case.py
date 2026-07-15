"""Caso de uso: cancelar uma Conta a Receber (`pending` → `cancelled`). Como nenhum
lançamento de fluxo de caixa foi gerado antes do recebimento, cancelar não precisa
estornar nada."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.finance.repositories.account_receivable_repository import (
    AccountReceivableRepository,
)
from app.modules.finance.schemas.account_receivable import AccountReceivableResponse
from app.modules.finance.use_cases._helpers import (
    ensure_receivable_transition_allowed,
    serialize_receivable,
)


class CancelAccountReceivableUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        receivable_id: uuid.UUID,
    ) -> AccountReceivableResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = AccountReceivableRepository(session)
            receivable = await repository.get_by_id(receivable_id)
            if receivable is None:
                raise NotFoundError(
                    "Conta a Receber não encontrada.", code="ACCOUNT_RECEIVABLE_NOT_FOUND"
                )
            ensure_receivable_transition_allowed(receivable, "cancelled")

            before = serialize_receivable(receivable)
            await repository.update(receivable, {"status": "cancelled"})

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="ACCOUNT_RECEIVABLE_CANCELLED",
                resource="finance",
                before=before,
                after=serialize_receivable(receivable),
            )
            await session.commit()

            return AccountReceivableResponse.model_validate(receivable)
