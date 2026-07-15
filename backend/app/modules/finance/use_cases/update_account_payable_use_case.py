"""Caso de uso: atualizar `due_date`/`amount` de uma Conta a Pagar — só permitido
enquanto `pending`. Nunca `status`/`payment_date`, que mudam por ações próprias
(`pay`/`cancel`)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.finance.repositories.account_payable_repository import (
    AccountPayableRepository,
)
from app.modules.finance.schemas.account_payable import (
    AccountPayableResponse,
    UpdateAccountPayableRequest,
)
from app.modules.finance.use_cases._helpers import ensure_payable_is_editable, serialize_payable


class UpdateAccountPayableUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payable_id: uuid.UUID,
        payload: UpdateAccountPayableRequest,
    ) -> AccountPayableResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = AccountPayableRepository(session)
            payable = await repository.get_by_id(payable_id)
            if payable is None:
                raise NotFoundError(
                    "Conta a Pagar não encontrada.", code="ACCOUNT_PAYABLE_NOT_FOUND"
                )
            ensure_payable_is_editable(payable)

            before = serialize_payable(payable)
            update_data = payload.model_dump(exclude_unset=True)
            await repository.update(payable, update_data)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="ACCOUNT_PAYABLE_UPDATED",
                resource="finance",
                before=before,
                after=serialize_payable(payable),
            )
            await session.commit()

            return AccountPayableResponse.model_validate(payable)
