"""Caso de uso: excluir um anexo. Remove do MinIO PRIMEIRO, só então a linha do banco —
nunca a ordem inversa, para nunca deixar uma linha "órfã" apontando para um objeto já
removido (se a remoção do MinIO falhar, a linha permanece e o anexo continua
consultável/baixável normalmente)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.core.storage import StorageClient
from app.modules.attachments.repositories.attachment_repository import AttachmentRepository


class DeleteAttachmentUseCase:
    def __init__(
        self, *, connection_manager: TenantConnectionManager, storage_client: StorageClient
    ) -> None:
        self._connections = connection_manager
        self._storage = storage_client

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        attachment_id: uuid.UUID,
    ) -> None:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = AttachmentRepository(session)
            attachment = await repository.get_by_id(attachment_id)
            if attachment is None:
                raise NotFoundError("Anexo não encontrado.", code="ATTACHMENT_NOT_FOUND")

            before = {
                "id": str(attachment.id),
                "resource_type": attachment.resource_type,
                "resource_id": str(attachment.resource_id),
                "original_filename": attachment.original_filename,
            }

            await self._storage.delete(attachment.storage_key)
            await repository.delete(attachment)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="ATTACHMENT_DELETED",
                resource="attachments",
                before=before,
            )
            await session.commit()
