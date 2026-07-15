"""Caso de uso: criar Conta a Pagar. Garante que `supplier_id` exista —
reaproveitando `GetSupplierUseCase` (nunca acessando o repository de outro módulo
diretamente, conforme `app/modules/README.md`)."""

from __future__ import annotations

import uuid

from veloai_shared.schema.tenant import AccountPayable

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.finance.repositories.account_payable_repository import (
    AccountPayableRepository,
)
from app.modules.finance.schemas.account_payable import (
    AccountPayableResponse,
    CreateAccountPayableRequest,
)
from app.modules.finance.use_cases._helpers import serialize_payable
from app.modules.suppliers.use_cases.get_supplier_use_case import GetSupplierUseCase


class CreateAccountPayableUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payload: CreateAccountPayableRequest,
    ) -> AccountPayableResponse:
        await GetSupplierUseCase(connection_manager=self._connections).execute(
            tenant_id=tenant_id, database_name=database_name, supplier_id=payload.supplier_id
        )

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = AccountPayableRepository(session)

            payable = AccountPayable(
                supplier_id=payload.supplier_id,
                due_date=payload.due_date,
                amount=payload.amount,
            )
            await repository.create(payable)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="ACCOUNT_PAYABLE_CREATED",
                resource="finance",
                after=serialize_payable(payable),
            )
            await session.commit()

            return AccountPayableResponse.model_validate(payable)
