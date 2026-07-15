"""Caso de uso: atualizar `due_date`/`amount` de uma Conta a Receber — só permitido
enquanto `pending` (depois de `received`/`cancelled` a conta está financeiramente
encerrada). Nunca `status`/`payment_date`, que mudam por ações próprias
(`receive`/`cancel`)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.finance.repositories.account_receivable_repository import (
    AccountReceivableRepository,
)
from app.modules.finance.schemas.account_receivable import (
    AccountReceivableResponse,
    UpdateAccountReceivableRequest,
)
from app.modules.finance.use_cases._helpers import (
    ensure_receivable_is_editable,
    serialize_receivable,
)


class UpdateAccountReceivableUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        receivable_id: uuid.UUID,
        payload: UpdateAccountReceivableRequest,
    ) -> AccountReceivableResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = AccountReceivableRepository(session)
            receivable = await repository.get_by_id(receivable_id)
            if receivable is None:
                raise NotFoundError(
                    "Conta a Receber não encontrada.", code="ACCOUNT_RECEIVABLE_NOT_FOUND"
                )
            ensure_receivable_is_editable(receivable)

            before = serialize_receivable(receivable)
            update_data = payload.model_dump(exclude_unset=True)
            await repository.update(receivable, update_data)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="ACCOUNT_RECEIVABLE_UPDATED",
                resource="finance",
                before=before,
                after=serialize_receivable(receivable),
            )
            await session.commit()

            return AccountReceivableResponse.model_validate(receivable)
