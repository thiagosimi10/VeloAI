"""Helper compartilhado pelos use cases de auth que devolvem `MeResponse`
(login/signup/me) — resolve a `storage_key` do avatar em uma URL assinada (o Storage é
privado, nunca expõe URLs públicas permanentes, conforme `app/core/storage.py`)."""

from __future__ import annotations

from app.core.storage import StorageClient


async def resolve_avatar_url(
    storage_client: StorageClient, avatar_key: str | None
) -> str | None:
    if avatar_key is None:
        return None
    return await storage_client.presigned_url(avatar_key)
