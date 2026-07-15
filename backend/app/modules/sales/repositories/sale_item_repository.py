"""Acesso ao banco do tenant para itens de Venda. Nenhuma regra de negócio aqui —
apenas persistência e consulta, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import SaleItem


class SaleItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, item_id: uuid.UUID) -> SaleItem | None:
        return await self._session.get(SaleItem, item_id)

    async def list_all_by_sale(self, sale_id: uuid.UUID) -> list[SaleItem]:
        result = await self._session.execute(
            select(SaleItem).where(SaleItem.sale_id == sale_id)
        )
        return list(result.scalars().all())

    async def create(self, item: SaleItem) -> SaleItem:
        self._session.add(item)
        await self._session.flush()
        return item

    async def delete(self, item: SaleItem) -> None:
        await self._session.delete(item)
        await self._session.flush()
