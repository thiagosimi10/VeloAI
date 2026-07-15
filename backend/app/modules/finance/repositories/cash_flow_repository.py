"""Acesso ao banco do tenant para Fluxo de Caixa. Nenhuma regra de negócio aqui —
apenas persistência e consulta, conforme 00-AI-CONSTITUTION.md. Sem `get_by_id`/
`update`/`delete` — `cash_flow` é um livro-razão só de criação e listagem (ver
`schemas/cash_flow.py`)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import CashFlowEntry

from app.modules.finance.schemas.cash_flow import CashFlowFilterParams


class CashFlowRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self, filters: CashFlowFilterParams) -> tuple[list[CashFlowEntry], int]:
        conditions = []
        if filters.type is not None:
            conditions.append(CashFlowEntry.type == filters.type)

        count_result = await self._session.execute(
            select(func.count()).select_from(CashFlowEntry).where(*conditions)
        )
        total = int(count_result.scalar_one())

        list_result = await self._session.execute(
            select(CashFlowEntry)
            .where(*conditions)
            .order_by(CashFlowEntry.date.desc(), CashFlowEntry.created_at.desc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(list_result.scalars().all()), total

    async def create(self, entry: CashFlowEntry) -> CashFlowEntry:
        self._session.add(entry)
        await self._session.flush()
        return entry
