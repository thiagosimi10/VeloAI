"""Acesso ao banco do tenant para a Base de Conhecimento (RAG — Fase 15). Nenhuma
regra de negócio aqui — apenas persistência e consulta, conforme
00-AI-CONSTITUTION.md."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import KnowledgeDocument


class KnowledgeDocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, document_id: uuid.UUID) -> KnowledgeDocument | None:
        result = await self._session.execute(
            select(KnowledgeDocument).where(
                KnowledgeDocument.id == document_id, KnowledgeDocument.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_titles_by_ids(self, document_ids: list[uuid.UUID]) -> dict[uuid.UUID, str]:
        result = await self._session.execute(
            select(KnowledgeDocument.id, KnowledgeDocument.title).where(
                KnowledgeDocument.id.in_(document_ids), KnowledgeDocument.deleted_at.is_(None)
            )
        )
        return {row.id: row.title for row in result.all()}

    async def list(self, *, page: int, page_size: int) -> tuple[list[KnowledgeDocument], int]:
        conditions = [KnowledgeDocument.deleted_at.is_(None)]

        count_result = await self._session.execute(
            select(func.count()).select_from(KnowledgeDocument).where(*conditions)
        )
        total = int(count_result.scalar_one())

        list_result = await self._session.execute(
            select(KnowledgeDocument)
            .where(*conditions)
            .order_by(KnowledgeDocument.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(list_result.scalars().all()), total

    async def create(self, document: KnowledgeDocument) -> KnowledgeDocument:
        self._session.add(document)
        await self._session.flush()
        return document

    async def soft_delete(self, document: KnowledgeDocument) -> None:
        document.deleted_at = datetime.now(UTC)
        await self._session.flush()
