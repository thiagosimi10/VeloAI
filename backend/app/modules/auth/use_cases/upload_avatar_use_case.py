"""Caso de uso: enviar/trocar a foto do próprio perfil. Diferente do módulo
`attachments/` (anexos vinculados a um recurso de negócio existente e listáveis em
lote), o avatar é 1-para-1 com o usuário — substitui o arquivo anterior no Storage em
vez de acumular histórico."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import AuthenticationError, ValidationError

from app.core.database import TenantConnectionManager
from app.core.logging import get_logger
from app.core.storage import StorageClient
from app.modules.auth.repositories.user_repository import TenantUserRepository

logger = get_logger(__name__)

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_MAX_AVATAR_SIZE_BYTES = 2 * 1024 * 1024


class UploadAvatarUseCase:
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
        user_id: uuid.UUID,
        content_type: str,
        data: bytes,
    ) -> str:
        if content_type not in _ALLOWED_CONTENT_TYPES:
            raise ValidationError(
                "Envie uma imagem JPEG, PNG ou WEBP.", code="UNSUPPORTED_FILE_FORMAT"
            )
        if len(data) > _MAX_AVATAR_SIZE_BYTES:
            raise ValidationError(
                "Imagem muito grande. O limite é 2MB.", code="AVATAR_FILE_TOO_LARGE"
            )

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            user_repository = TenantUserRepository(session)
            user = await user_repository.get_by_id(user_id)
            if user is None:
                raise AuthenticationError("Usuário não encontrado.", code="NOT_AUTHENTICATED")

            previous_key = user.avatar_key
            extension = content_type.removeprefix("image/")
            avatar_key = f"avatars/{tenant_id}/{user_id}/{uuid.uuid4()}.{extension}"

            await self._storage.upload(avatar_key, data, content_type=content_type)
            await user_repository.update_avatar(user, avatar_key)
            await session.commit()

        if previous_key is not None:
            try:
                await self._storage.delete(previous_key)
            except Exception:  # noqa: BLE001 - limpeza best-effort, o avatar novo já está salvo
                logger.warning("avatar_previous_cleanup_failed", avatar_key=previous_key)

        return avatar_key
