"""Caso de uso: criar Conta a Receber. Garante que `customer_id` exista —
reaproveitando `GetCustomerUseCase` (nunca acessando o repository de outro módulo
diretamente, conforme `app/modules/README.md`)."""

from __future__ import annotations

import uuid

from veloai_shared.schema.tenant import AccountReceivable

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.customers.use_cases.get_customer_use_case import GetCustomerUseCase
from app.modules.finance.repositories.account_receivable_repository import (
    AccountReceivableRepository,
)
from app.modules.finance.schemas.account_receivable import (
    AccountReceivableResponse,
    CreateAccountReceivableRequest,
)
from app.modules.finance.use_cases._helpers import serialize_receivable


class CreateAccountReceivableUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payload: CreateAccountReceivableRequest,
    ) -> AccountReceivableResponse:
        await GetCustomerUseCase(connection_manager=self._connections).execute(
            tenant_id=tenant_id, database_name=database_name, customer_id=payload.customer_id
        )

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = AccountReceivableRepository(session)

            receivable = AccountReceivable(
                customer_id=payload.customer_id,
                due_date=payload.due_date,
                amount=payload.amount,
            )
            await repository.create(receivable)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="ACCOUNT_RECEIVABLE_CREATED",
                resource="finance",
                after=serialize_receivable(receivable),
            )
            await session.commit()

            return AccountReceivableResponse.model_validate(receivable)
