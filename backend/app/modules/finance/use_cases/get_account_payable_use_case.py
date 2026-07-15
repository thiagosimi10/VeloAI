"""Caso de uso: buscar uma Conta a Pagar pelo id."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import TenantConnectionManager
from app.modules.finance.repositories.account_payable_repository import (
    AccountPayableRepository,
)
from app.modules.finance.schemas.account_payable import AccountPayableResponse


class GetAccountPayableUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, payable_id: uuid.UUID
    ) -> AccountPayableResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            payable = await AccountPayableRepository(session).get_by_id(payable_id)
            if payable is None:
                raise NotFoundError(
                    "Conta a Pagar não encontrada.", code="ACCOUNT_PAYABLE_NOT_FOUND"
                )
            return AccountPayableResponse.model_validate(payable)
