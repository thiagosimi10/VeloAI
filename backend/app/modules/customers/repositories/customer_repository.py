"""Acesso ao banco do tenant para Clientes. Nenhuma regra de negócio aqui — apenas
persistência e consulta, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import Customer

from app.modules.customers.schemas.customer import CustomerFilterParams

_SORT_COLUMNS = {
    "name": Customer.name,
    "code": Customer.code,
    "created_at": Customer.created_at,
}


class CustomerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, customer_id: uuid.UUID) -> Customer | None:
        result = await self._session.execute(
            select(Customer).where(Customer.id == customer_id, Customer.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_document(self, document: str) -> Customer | None:
        result = await self._session.execute(
            select(Customer).where(
                Customer.document == document, Customer.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def count_all(self) -> int:
        """Conta TODOS os registros, incluindo os excluídos (soft delete) — usado para
        gerar o próximo `code` sequencial. `code` é único na tabela inteira, então a
        contagem não pode ignorar linhas excluídas sob pena de gerar um valor
        duplicado."""

        result = await self._session.execute(select(func.count()).select_from(Customer))
        return int(result.scalar_one())

    async def list(self, filters: CustomerFilterParams) -> tuple[list[Customer], int]:
        conditions = [Customer.deleted_at.is_(None)]
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    Customer.name.ilike(pattern),
                    Customer.document.ilike(pattern),
                    Customer.email.ilike(pattern),
                )
            )

        count_result = await self._session.execute(
            select(func.count()).select_from(Customer).where(*conditions)
        )
        total = int(count_result.scalar_one())

        sort_column = _SORT_COLUMNS[filters.sort]
        order_by = sort_column.asc() if filters.order == "asc" else sort_column.desc()

        list_result = await self._session.execute(
            select(Customer)
            .where(*conditions)
            .order_by(order_by)
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(list_result.scalars().all()), total

    async def create(self, customer: Customer) -> Customer:
        self._session.add(customer)
        await self._session.flush()
        return customer

    async def update(self, customer: Customer, data: dict[str, Any]) -> Customer:
        for field, value in data.items():
            setattr(customer, field, value)
        await self._session.flush()
        return customer

    async def soft_delete(self, customer: Customer) -> None:
        customer.deleted_at = datetime.now(UTC)
        customer.active = False
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()
