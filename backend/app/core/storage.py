"""Cliente MinIO (Storage — Fase 12), conforme `docs/22-API-STANDARDS.md` ("Nunca
armazenar arquivos no banco"). Infraestrutura cross-cutting (mesmo nível de
`app/core/database.py`/`app/core/audit.py`) — qualquer módulo futuro que precise
armazenar arquivos (ex.: imagem de Produto) pode reutilizar este cliente diretamente,
sem depender do módulo `attachments/`.

O SDK oficial (`minio`) é síncrono — todo método aqui despacha a chamada bloqueante
para uma thread (`asyncio.to_thread`) para não bloquear o event loop do FastAPI."""

from __future__ import annotations

import asyncio
import io
from datetime import timedelta
from functools import lru_cache

from minio import Minio

from app.core.config import get_settings


class StorageClient:
    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        secure: bool,
        bucket_name: str,
    ) -> None:
        self._bucket_name = bucket_name
        self._client = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=secure
        )

    def _ensure_bucket_exists_sync(self) -> None:
        if not self._client.bucket_exists(self._bucket_name):
            self._client.make_bucket(self._bucket_name)

    async def ensure_bucket_exists(self) -> None:
        await asyncio.to_thread(self._ensure_bucket_exists_sync)

    async def upload(self, key: str, data: bytes, *, content_type: str) -> None:
        await asyncio.to_thread(
            self._client.put_object,
            self._bucket_name,
            key,
            io.BytesIO(data),
            len(data),
            content_type=content_type,
        )

    async def delete(self, key: str) -> None:
        await asyncio.to_thread(self._client.remove_object, self._bucket_name, key)

    async def presigned_url(self, key: str, *, expires_seconds: int = 3600) -> str:
        return await asyncio.to_thread(
            self._client.presigned_get_object,
            self._bucket_name,
            key,
            timedelta(seconds=expires_seconds),
        )

    async def is_reachable(self) -> bool:
        try:
            await asyncio.to_thread(self._client.bucket_exists, self._bucket_name)
            return True
        except Exception:  # noqa: BLE001 - readiness apenas reporta indisponibilidade
            return False


@lru_cache
def get_storage_client() -> StorageClient:
    """Retorna a instância única (cacheada) de `StorageClient`, mesmo padrão de
    `get_settings()`."""

    settings = get_settings()
    return StorageClient(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_use_ssl,
        bucket_name=settings.minio_bucket_name,
    )
