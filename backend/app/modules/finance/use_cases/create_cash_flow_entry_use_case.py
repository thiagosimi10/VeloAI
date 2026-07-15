"""Caso de uso: criar um lançamento avulso de Fluxo de Caixa (11-FINANCEIRO.md:
"Lançamentos Avulsos"). Um "estorno" é simplesmente um novo lançamento com o tipo
oposto — não há coluna para linkar ao lançamento original."""

from __future__ import annotations

import uuid
from datetime import date

from veloai_shared.schema.tenant import CashFlowEntry

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.finance.repositories.cash_flow_repository import CashFlowRepository
from app.modules.finance.schemas.cash_flow import CashFlowEntryResponse, CreateCashFlowEntryRequest


class CreateCashFlowEntryUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payload: CreateCashFlowEntryRequest,
    ) -> CashFlowEntryResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            entry = CashFlowEntry(
                type=payload.type,
                category=payload.category,
                description=payload.description,
                amount=payload.amount,
                date=payload.date or date.today(),
            )
            await CashFlowRepository(session).create(entry)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="CASH_FLOW_ENTRY_CREATED",
                resource="finance",
                after=CashFlowEntryResponse.model_validate(entry).model_dump(mode="json"),
            )
            await session.commit()

            return CashFlowEntryResponse.model_validate(entry)
