"""Caso de uso: pagar uma Conta a Pagar (`pending` → `paid`). Registra `payment_date` e
insere automaticamente uma entrada em `cash_flow` (`type="out"`) na MESMA transação —
"Pagamento → Atualizar Fluxo" (11-FINANCEIRO.md). Espelho de
`receive_account_receivable_use_case.py`."""

from __future__ import annotations

import uuid
from datetime import date

from veloai_shared.exceptions import NotFoundError
from veloai_shared.schema.tenant import CashFlowEntry

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.finance.repositories.account_payable_repository import (
    AccountPayableRepository,
)
from app.modules.finance.repositories.cash_flow_repository import CashFlowRepository
from app.modules.finance.schemas.account_payable import AccountPayableResponse
from app.modules.finance.use_cases._helpers import (
    ensure_payable_transition_allowed,
    serialize_payable,
)


class PayAccountPayableUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payable_id: uuid.UUID,
    ) -> AccountPayableResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = AccountPayableRepository(session)
            payable = await repository.get_by_id(payable_id)
            if payable is None:
                raise NotFoundError(
                    "Conta a Pagar não encontrada.", code="ACCOUNT_PAYABLE_NOT_FOUND"
                )
            ensure_payable_transition_allowed(payable, "paid")

            before = serialize_payable(payable)
            today = date.today()
            await repository.update(payable, {"status": "paid", "payment_date": today})

            await CashFlowRepository(session).create(
                CashFlowEntry(
                    type="out",
                    category="Pagamento",
                    description=f"Pagamento da Conta a Pagar {payable.id}",
                    amount=payable.amount,
                    date=today,
                )
            )

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="ACCOUNT_PAYABLE_PAID",
                resource="finance",
                before=before,
                after=serialize_payable(payable),
            )
            await session.commit()

            return AccountPayableResponse.model_validate(payable)
