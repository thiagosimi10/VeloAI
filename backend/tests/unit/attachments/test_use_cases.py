import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import NotFoundError

from app.modules.attachments.schemas.attachment import AttachmentFilterParams
from app.modules.attachments.use_cases.delete_attachment_use_case import (
    DeleteAttachmentUseCase,
)
from app.modules.attachments.use_cases.list_attachments_use_case import ListAttachmentsUseCase
from app.modules.attachments.use_cases.upload_attachment_use_case import (
    UploadAttachmentUseCase,
)


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


def _build_storage_client_mock() -> MagicMock:
    storage = MagicMock()
    storage.upload = AsyncMock()
    storage.delete = AsyncMock()
    storage.presigned_url = AsyncMock(return_value="https://minio.test/presigned-url")
    return storage


def _build_attachment_mock(**overrides: object) -> MagicMock:
    attachment = MagicMock()
    attachment.id = overrides.get("id", uuid.uuid4())
    attachment.resource_type = overrides.get("resource_type", "service_order")
    attachment.resource_id = overrides.get("resource_id", uuid.uuid4())
    attachment.original_filename = overrides.get("original_filename", "foto.jpg")
    attachment.storage_key = overrides.get("storage_key", "tenant-abc/service_order/x/foto.jpg")
    attachment.content_type = overrides.get("content_type", "image/jpeg")
    attachment.size_bytes = overrides.get("size_bytes", 1024)
    attachment.uploaded_by = overrides.get("uploaded_by", uuid.uuid4())
    attachment.created_at = overrides.get("created_at", datetime.now(UTC))
    return attachment


async def test_upload_attachment_rejects_nonexistent_resource() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    storage_client = _build_storage_client_mock()
    use_case = UploadAttachmentUseCase(
        connection_manager=connection_manager, storage_client=storage_client
    )

    with patch(
        "app.modules.attachments.use_cases.upload_attachment_use_case.ensure_resource_exists",
        AsyncMock(
            side_effect=NotFoundError(
                "Ordem de Serviço não encontrada.", code="SERVICE_ORDER_NOT_FOUND"
            )
        ),
    ):
        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                resource_type="service_order",
                resource_id=uuid.uuid4(),
                original_filename="foto.jpg",
                content_type="image/jpeg",
                data=b"fake-image-bytes",
            )

    storage_client.upload.assert_not_awaited()


async def test_upload_attachment_uploads_then_persists_metadata() -> None:
    session = AsyncMock()
    connection_manager = _connection_manager_with_session(session)
    storage_client = _build_storage_client_mock()
    use_case = UploadAttachmentUseCase(
        connection_manager=connection_manager, storage_client=storage_client
    )
    tenant_id = uuid.uuid4()
    resource_id = uuid.uuid4()

    async def _fake_create(attachment: object) -> object:
        attachment.id = uuid.uuid4()  # type: ignore[attr-defined]
        attachment.created_at = datetime.now(UTC)  # type: ignore[attr-defined]
        return attachment

    with (
        patch(
            "app.modules.attachments.use_cases.upload_attachment_use_case.ensure_resource_exists",
            AsyncMock(),
        ),
        patch(
            "app.modules.attachments.use_cases.upload_attachment_use_case.AttachmentRepository"
        ) as repo_cls,
        patch(
            "app.modules.attachments.use_cases.upload_attachment_use_case.record_audit_log",
            AsyncMock(),
        ),
    ):
        repo_cls.return_value.create = AsyncMock(side_effect=_fake_create)

        result = await use_case.execute(
            tenant_id=tenant_id,
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            resource_type="service_order",
            resource_id=resource_id,
            original_filename="foto.jpg",
            content_type="image/jpeg",
            data=b"fake-image-bytes",
        )

    storage_client.upload.assert_awaited_once()
    uploaded_key = storage_client.upload.call_args.args[0]
    assert uploaded_key.startswith(f"{tenant_id}/service_order/{resource_id}/")
    assert uploaded_key.endswith("_foto.jpg")
    assert result.size_bytes == len(b"fake-image-bytes")
    assert result.url == "https://minio.test/presigned-url"


async def test_list_attachments_builds_presigned_url_for_each_item() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    storage_client = _build_storage_client_mock()
    use_case = ListAttachmentsUseCase(
        connection_manager=connection_manager, storage_client=storage_client
    )
    attachment = _build_attachment_mock()

    with patch(
        "app.modules.attachments.use_cases.list_attachments_use_case.AttachmentRepository"
    ) as repo_cls:
        repo_cls.return_value.list_by_resource = AsyncMock(return_value=[attachment])

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=AttachmentFilterParams(
                resource_type="service_order", resource_id=attachment.resource_id
            ),
        )

    assert len(result) == 1
    assert result[0].url == "https://minio.test/presigned-url"
    storage_client.presigned_url.assert_awaited_once_with(attachment.storage_key)


async def test_delete_attachment_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    storage_client = _build_storage_client_mock()
    use_case = DeleteAttachmentUseCase(
        connection_manager=connection_manager, storage_client=storage_client
    )

    with patch(
        "app.modules.attachments.use_cases.delete_attachment_use_case.AttachmentRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                attachment_id=uuid.uuid4(),
            )

    storage_client.delete.assert_not_awaited()


async def test_delete_attachment_removes_from_storage_before_deleting_row() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    storage_client = _build_storage_client_mock()
    use_case = DeleteAttachmentUseCase(
        connection_manager=connection_manager, storage_client=storage_client
    )
    attachment = _build_attachment_mock()

    call_order: list[str] = []
    storage_client.delete.side_effect = lambda _key: call_order.append("storage_delete")

    with (
        patch(
            "app.modules.attachments.use_cases.delete_attachment_use_case.AttachmentRepository"
        ) as repo_cls,
        patch(
            "app.modules.attachments.use_cases.delete_attachment_use_case.record_audit_log",
            AsyncMock(),
        ),
    ):
        repo_cls.return_value.get_by_id = AsyncMock(return_value=attachment)

        async def _fake_delete(_attachment: object) -> None:
            call_order.append("row_delete")

        repo_cls.return_value.delete = AsyncMock(side_effect=_fake_delete)

        await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            attachment_id=attachment.id,
        )

    assert call_order == ["storage_delete", "row_delete"]
