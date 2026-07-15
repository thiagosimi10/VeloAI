"""Acesso ao banco do tenant para Anexos. Nenhuma regra de negócio aqui — apenas
persistência e consulta, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import Attachment


class AttachmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, attachment_id: uuid.UUID) -> Attachment | None:
        return await self._session.get(Attachment, attachment_id)

    async def list_by_resource(
        self, resource_type: str, resource_id: uuid.UUID
    ) -> list[Attachment]:
        result = await self._session.execute(
            select(Attachment)
            .where(
                Attachment.resource_type == resource_type,
                Attachment.resource_id == resource_id,
            )
            .order_by(Attachment.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, attachment: Attachment) -> Attachment:
        self._session.add(attachment)
        await self._session.flush()
        return attachment

    async def delete(self, attachment: Attachment) -> None:
        await self._session.delete(attachment)
        await self._session.flush()
