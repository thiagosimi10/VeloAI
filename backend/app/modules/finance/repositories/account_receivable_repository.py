"""Acesso ao banco do tenant para Contas a Receber. Nenhuma regra de negócio aqui —
apenas persistência e consulta, conforme 00-AI-CONSTITUTION.md. Sem `soft_delete()` —
conta nunca é excluída, só cancelada (`status="cancelled"`, via `update`)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import AccountReceivable

from app.modules.finance.schemas.account_receivable import AccountReceivableFilterParams


class AccountReceivableRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, receivable_id: uuid.UUID) -> AccountReceivable | None:
        result = await self._session.execute(
            select(AccountReceivable).where(
                AccountReceivable.id == receivable_id, AccountReceivable.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self, filters: AccountReceivableFilterParams
    ) -> tuple[list[AccountReceivable], int]:
        conditions = [AccountReceivable.deleted_at.is_(None)]
        if filters.customer_id is not None:
            conditions.append(AccountReceivable.customer_id == filters.customer_id)
        if filters.status is not None:
            conditions.append(AccountReceivable.status == filters.status)

        count_result = await self._session.execute(
            select(func.count()).select_from(AccountReceivable).where(*conditions)
        )
        total = int(count_result.scalar_one())

        list_result = await self._session.execute(
            select(AccountReceivable)
            .where(*conditions)
            .order_by(AccountReceivable.due_date.asc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(list_result.scalars().all()), total

    async def create(self, receivable: AccountReceivable) -> AccountReceivable:
        self._session.add(receivable)
        await self._session.flush()
        return receivable

    async def update(
        self, receivable: AccountReceivable, data: dict[str, Any]
    ) -> AccountReceivable:
        for field, value in data.items():
            setattr(receivable, field, value)
        await self._session.flush()
        return receivable
