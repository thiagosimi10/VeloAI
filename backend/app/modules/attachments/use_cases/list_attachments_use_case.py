"""Caso de uso: listar os anexos de um recurso (sem paginação — não se espera um
volume grande de anexos por Cliente/Produto/Ordem de Serviço nesta fase)."""

from __future__ import annotations

import uuid

from app.core.database import TenantConnectionManager
from app.core.storage import StorageClient
from app.modules.attachments.repositories.attachment_repository import AttachmentRepository
from app.modules.attachments.schemas.attachment import (
    AttachmentFilterParams,
    AttachmentResponse,
)


class ListAttachmentsUseCase:
    def __init__(
        self, *, connection_manager: TenantConnectionManager, storage_client: StorageClient
    ) -> None:
        self._connections = connection_manager
        self._storage = storage_client

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, filters: AttachmentFilterParams
    ) -> list[AttachmentResponse]:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            attachments = await AttachmentRepository(session).list_by_resource(
                filters.resource_type, filters.resource_id
            )

        responses: list[AttachmentResponse] = []
        for attachment in attachments:
            url = await self._storage.presigned_url(attachment.storage_key)
            responses.append(
                AttachmentResponse(
                    id=attachment.id,
                    resource_type=attachment.resource_type,
                    resource_id=attachment.resource_id,
                    original_filename=attachment.original_filename,
                    content_type=attachment.content_type,
                    size_bytes=attachment.size_bytes,
                    url=url,
                    uploaded_by=attachment.uploaded_by,
                    created_at=attachment.created_at,
                )
            )
        return responses
