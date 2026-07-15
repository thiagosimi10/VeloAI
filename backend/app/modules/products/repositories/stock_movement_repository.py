"""Acesso ao banco do tenant para o histórico de movimentações de estoque. Nenhuma
regra de negócio aqui — apenas persistência e consulta, conforme
00-AI-CONSTITUTION.md. Append-only: não existe `update`/`soft_delete` (ver
`veloai_shared/schema/tenant/stock_movement.py`)."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import StockMovement

from app.modules.products.schemas.stock_movement import StockMovementFilterParams


class StockMovementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, movement: StockMovement) -> StockMovement:
        self._session.add(movement)
        await self._session.flush()
        return movement

    async def list_by_product(
        self, product_id: uuid.UUID, filters: StockMovementFilterParams
    ) -> tuple[list[StockMovement], int]:
        conditions = [StockMovement.product_id == product_id]

        count_result = await self._session.execute(
            select(func.count()).select_from(StockMovement).where(*conditions)
        )
        total = int(count_result.scalar_one())

        list_result = await self._session.execute(
            select(StockMovement)
            .where(*conditions)
            .order_by(StockMovement.created_at.desc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(list_result.scalars().all()), total
