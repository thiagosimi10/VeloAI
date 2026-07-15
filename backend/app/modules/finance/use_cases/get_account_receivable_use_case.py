"""Caso de uso: buscar uma Conta a Receber pelo id."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import TenantConnectionManager
from app.modules.finance.repositories.account_receivable_repository import (
    AccountReceivableRepository,
)
from app.modules.finance.schemas.account_receivable import AccountReceivableResponse


class GetAccountReceivableUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, receivable_id: uuid.UUID
    ) -> AccountReceivableResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            receivable = await AccountReceivableRepository(session).get_by_id(receivable_id)
            if receivable is None:
                raise NotFoundError(
                    "Conta a Receber não encontrada.", code="ACCOUNT_RECEIVABLE_NOT_FOUND"
                )
            return AccountReceivableResponse.model_validate(receivable)
