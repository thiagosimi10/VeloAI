"""Acesso ao banco do tenant para Contas a Pagar. Espelho de
`account_receivable_repository.py`, trocando `customer_id` por `supplier_id`."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import AccountPayable

from app.modules.finance.schemas.account_payable import AccountPayableFilterParams


class AccountPayableRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, payable_id: uuid.UUID) -> AccountPayable | None:
        result = await self._session.execute(
            select(AccountPayable).where(
                AccountPayable.id == payable_id, AccountPayable.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self, filters: AccountPayableFilterParams
    ) -> tuple[list[AccountPayable], int]:
        conditions = [AccountPayable.deleted_at.is_(None)]
        if filters.supplier_id is not None:
            conditions.append(AccountPayable.supplier_id == filters.supplier_id)
        if filters.status is not None:
            conditions.append(AccountPayable.status == filters.status)

        count_result = await self._session.execute(
            select(func.count()).select_from(AccountPayable).where(*conditions)
        )
        total = int(count_result.scalar_one())

        list_result = await self._session.execute(
            select(AccountPayable)
            .where(*conditions)
            .order_by(AccountPayable.due_date.asc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(list_result.scalars().all()), total

    async def create(self, payable: AccountPayable) -> AccountPayable:
        self._session.add(payable)
        await self._session.flush()
        return payable

    async def update(self, payable: AccountPayable, data: dict[str, Any]) -> AccountPayable:
        for field, value in data.items():
            setattr(payable, field, value)
        await self._session.flush()
        return payable
