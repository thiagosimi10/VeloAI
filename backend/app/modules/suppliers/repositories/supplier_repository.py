"""Acesso ao banco do tenant para Fornecedores. Nenhuma regra de negócio aqui — apenas
persistência e consulta, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import Supplier

from app.modules.suppliers.schemas.supplier import SupplierFilterParams

_SORT_COLUMNS = {
    "name": Supplier.name,
    "code": Supplier.code,
    "created_at": Supplier.created_at,
}


class SupplierRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, supplier_id: uuid.UUID) -> Supplier | None:
        result = await self._session.execute(
            select(Supplier).where(Supplier.id == supplier_id, Supplier.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_document(self, document: str) -> Supplier | None:
        result = await self._session.execute(
            select(Supplier).where(
                Supplier.document == document, Supplier.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def count_all(self) -> int:
        """Conta TODOS os registros, incluindo os excluídos (soft delete) — usado para
        gerar o próximo `code` sequencial. `code` é único na tabela inteira, então a
        contagem não pode ignorar linhas excluídas sob pena de gerar um valor
        duplicado."""

        result = await self._session.execute(select(func.count()).select_from(Supplier))
        return int(result.scalar_one())

    async def list(self, filters: SupplierFilterParams) -> tuple[list[Supplier], int]:
        conditions = [Supplier.deleted_at.is_(None)]
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    Supplier.name.ilike(pattern),
                    Supplier.document.ilike(pattern),
                    Supplier.email.ilike(pattern),
                )
            )

        count_result = await self._session.execute(
            select(func.count()).select_from(Supplier).where(*conditions)
        )
        total = int(count_result.scalar_one())

        sort_column = _SORT_COLUMNS[filters.sort]
        order_by = sort_column.asc() if filters.order == "asc" else sort_column.desc()

        list_result = await self._session.execute(
            select(Supplier)
            .where(*conditions)
            .order_by(order_by)
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(list_result.scalars().all()), total

    async def create(self, supplier: Supplier) -> Supplier:
        self._session.add(supplier)
        await self._session.flush()
        return supplier

    async def update(self, supplier: Supplier, data: dict[str, Any]) -> Supplier:
        for field, value in data.items():
            setattr(supplier, field, value)
        await self._session.flush()
        return supplier

    async def soft_delete(self, supplier: Supplier) -> None:
        supplier.deleted_at = datetime.now(UTC)
        supplier.active = False
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()
