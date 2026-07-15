"""Controller do módulo de Anexos. Responsabilidade: receber requisição, validar
permissão via `require_permission` e delegar ao Use Case — nunca conter regra de
negócio (00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from veloai_shared.responses import SuccessResponse

from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.core.storage import StorageClient, get_storage_client
from app.modules.attachments.permissions import (
    ATTACHMENTS_DELETE,
    ATTACHMENTS_UPLOAD,
    ATTACHMENTS_VIEW,
)
from app.modules.attachments.schemas.attachment import (
    AttachmentFilterParams,
    AttachmentResourceType,
    AttachmentResponse,
)
from app.modules.attachments.use_cases.delete_attachment_use_case import (
    DeleteAttachmentUseCase,
)
from app.modules.attachments.use_cases.list_attachments_use_case import ListAttachmentsUseCase
from app.modules.attachments.use_cases.upload_attachment_use_case import (
    UploadAttachmentUseCase,
)

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.get("")
async def list_attachments(
    filters: AttachmentFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(ATTACHMENTS_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
    storage_client: StorageClient = Depends(get_storage_client),
) -> SuccessResponse[list[AttachmentResponse]]:
    use_case = ListAttachmentsUseCase(
        connection_manager=connection_manager, storage_client=storage_client
    )
    attachments = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(message="Anexos listados com sucesso.", data=attachments)


@router.post("", status_code=201)
async def upload_attachment(
    resource_type: AttachmentResourceType = Form(...),
    resource_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_permission(ATTACHMENTS_UPLOAD)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
    storage_client: StorageClient = Depends(get_storage_client),
) -> SuccessResponse[AttachmentResponse]:
    data = await file.read()
    use_case = UploadAttachmentUseCase(
        connection_manager=connection_manager, storage_client=storage_client
    )
    attachment = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        original_filename=file.filename or "arquivo",
        content_type=file.content_type or "application/octet-stream",
        data=data,
    )
    return SuccessResponse(message="Anexo enviado com sucesso.", data=attachment)


@router.delete("/{attachment_id}")
async def delete_attachment(
    attachment_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(ATTACHMENTS_DELETE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
    storage_client: StorageClient = Depends(get_storage_client),
) -> SuccessResponse[dict[str, str]]:
    use_case = DeleteAttachmentUseCase(
        connection_manager=connection_manager, storage_client=storage_client
    )
    await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        attachment_id=attachment_id,
    )
    return SuccessResponse(message="Anexo removido com sucesso.", data={})
