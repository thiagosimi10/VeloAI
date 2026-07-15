"""Caso de uso: receber uma Conta a Receber (`pending` → `received`). Registra
`payment_date` e insere automaticamente uma entrada em `cash_flow` (`type="in"`) na
MESMA transação — "Recebimento → Atualizar Fluxo" (11-FINANCEIRO.md). Como
`AccountReceivable` e `CashFlowEntry` vivem no mesmo módulo (`finance/`), essa
integração não esbarra na regra de "nunca acessar repository de outro módulo"."""

from __future__ import annotations

import uuid
from datetime import date

from veloai_shared.exceptions import NotFoundError
from veloai_shared.schema.tenant import CashFlowEntry

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.finance.repositories.account_receivable_repository import (
    AccountReceivableRepository,
)
from app.modules.finance.repositories.cash_flow_repository import CashFlowRepository
from app.modules.finance.schemas.account_receivable import AccountReceivableResponse
from app.modules.finance.use_cases._helpers import (
    ensure_receivable_transition_allowed,
    serialize_receivable,
)


class ReceiveAccountReceivableUseCase:
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
            ensure_receivable_transition_allowed(receivable, "received")

            before = serialize_receivable(receivable)
            today = date.today()
            await repository.update(receivable, {"status": "received", "payment_date": today})

            await CashFlowRepository(session).create(
                CashFlowEntry(
                    type="in",
                    category="Recebimento",
                    description=f"Recebimento da Conta a Receber {receivable.id}",
                    amount=receivable.amount,
                    date=today,
                )
            )

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="ACCOUNT_RECEIVABLE_RECEIVED",
                resource="finance",
                before=before,
                after=serialize_receivable(receivable),
            )
            await session.commit()

            return AccountReceivableResponse.model_validate(receivable)
