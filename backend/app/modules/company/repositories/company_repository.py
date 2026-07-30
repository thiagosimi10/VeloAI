"""Acesso à linha única de `companies` do tenant. Nenhuma regra de negócio aqui —
apenas persistência e consulta, conforme 00-AI-CONSTITUTION.md ("Repositories: Nunca
validar regras.")."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import Company


class CompanyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_the_company(self) -> Company | None:
        """Cada banco de tenant tem exatamente uma linha em `companies` (semeada pelo
        Provisioning Service) — nunca há necessidade de filtrar por id."""

        result = await self._session.execute(select(Company).limit(1))
        return result.scalars().first()

    async def update(self, company: Company, data: dict[str, Any]) -> Company:
        for field, value in data.items():
            setattr(company, field, value)
        await self._session.flush()
        return company
