"""Acesso ao banco do tenant para Vendas. Nenhuma regra de negócio aqui — apenas
persistência e consulta, conforme 00-AI-CONSTITUTION.md. Sem `count_all()` (não há
número sequencial) e sem `soft_delete()` (venda nunca é excluída, só cancelada)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import Sale

from app.modules.sales.schemas.sale import SaleFilterParams


class SaleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, sale_id: uuid.UUID) -> Sale | None:
        result = await self._session.execute(
            select(Sale).where(Sale.id == sale_id, Sale.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list(self, filters: SaleFilterParams) -> tuple[list[Sale], int]:
        conditions = [Sale.deleted_at.is_(None)]
        if filters.customer_id is not None:
            conditions.append(Sale.customer_id == filters.customer_id)
        if filters.status is not None:
            conditions.append(Sale.status == filters.status)

        count_result = await self._session.execute(
            select(func.count()).select_from(Sale).where(*conditions)
        )
        total = int(count_result.scalar_one())

        list_result = await self._session.execute(
            select(Sale)
            .where(*conditions)
            .order_by(Sale.created_at.desc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(list_result.scalars().all()), total

    async def create(self, sale: Sale) -> Sale:
        self._session.add(sale)
        await self._session.flush()
        return sale

    async def update(self, sale: Sale, data: dict[str, Any]) -> Sale:
        for field, value in data.items():
            setattr(sale, field, value)
        await self._session.flush()
        return sale

    async def commit(self) -> None:
        await self._session.commit()
