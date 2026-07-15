"""Caso de uso: enviar um anexo para um recurso existente. A `storage_key` é sempre
prefixada com `tenant_id`/um uuid novo — nunca derivada só do nome original do arquivo,
evitando colisão e vazamento entre tenants (bucket único, ver `app/core/storage.py`)."""

from __future__ import annotations

import uuid

from veloai_shared.schema.tenant import Attachment

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.core.storage import StorageClient
from app.modules.attachments.repositories.attachment_repository import AttachmentRepository
from app.modules.attachments.schemas.attachment import (
    AttachmentResourceType,
    AttachmentResponse,
)
from app.modules.attachments.use_cases._helpers import ensure_resource_exists


class UploadAttachmentUseCase:
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
        resource_type: AttachmentResourceType,
        resource_id: uuid.UUID,
        original_filename: str,
        content_type: str,
        data: bytes,
    ) -> AttachmentResponse:
        await ensure_resource_exists(
            connection_manager=self._connections,
            resource_type=resource_type,
            resource_id=resource_id,
            tenant_id=tenant_id,
            database_name=database_name,
        )

        storage_key = f"{tenant_id}/{resource_type}/{resource_id}/{uuid.uuid4()}_{original_filename}"
        await self._storage.upload(storage_key, data, content_type=content_type)

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            attachment = Attachment(
                resource_type=resource_type,
                resource_id=resource_id,
                original_filename=original_filename,
                storage_key=storage_key,
                content_type=content_type,
                size_bytes=len(data),
                uploaded_by=actor_user_id,
            )
            await AttachmentRepository(session).create(attachment)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="ATTACHMENT_UPLOADED",
                resource="attachments",
                after={
                    "id": str(attachment.id),
                    "resource_type": resource_type,
                    "resource_id": str(resource_id),
                    "original_filename": original_filename,
                },
            )
            await session.commit()

            url = await self._storage.presigned_url(storage_key)
            return AttachmentResponse(
                id=attachment.id,
                resource_type=resource_type,
                resource_id=resource_id,
                original_filename=original_filename,
                content_type=content_type,
                size_bytes=attachment.size_bytes,
                url=url,
                uploaded_by=actor_user_id,
                created_at=attachment.created_at,
            )
