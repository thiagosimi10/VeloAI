"""Guarda transitória (Redis, TTL curto) de arquivos anexados na conversa com a IA —
diferente de `Attachment` (`app/modules/attachments/`), que é permanente e vinculado a
um recurso já existente, este arquivo só existe até a IA decidir importar (uma das
Tools `Import{Products,Customers,Suppliers,Categories}FromFile`) ou até expirar sem
uso, conforme docs/20-MCP-TOOLS.md."""

from __future__ import annotations

import base64
import json
import uuid
from typing import Any

from redis.asyncio import Redis

from app.core.rate_limit import get_redis_client
from app.core.spreadsheet_parser import read_raw_preview

_TTL_SECONDS = 900


class AiUploadStore:
    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client

    async def save(self, *, tenant_id: str, filename: str, data: bytes) -> str:
        upload_id = str(uuid.uuid4())
        payload = json.dumps(
            {"filename": filename, "data": base64.b64encode(data).decode("ascii")}
        )
        await self._redis.set(self._redis_key(tenant_id, upload_id), payload, ex=_TTL_SECONDS)
        return upload_id

    async def preview(self, *, tenant_id: str, upload_id: str) -> dict[str, Any] | None:
        """Lê só o cabeçalho bruto (sem mapear para nenhum campo de nenhum módulo
        específico) + a contagem de linhas — monta um resumo leve que vai no prompt da
        IA, para ela decidir sozinha (pelo texto do pedido + esses nomes de coluna) se é
        uma importação de Produtos, Clientes, Fornecedores ou Categorias, e qual Tool
        chamar. Nunca envia o conteúdo bruto do arquivo à LLM."""

        stored = await self._read(tenant_id, upload_id)
        if stored is None:
            return None
        filename, file_bytes = stored
        headers, row_count = read_raw_preview(filename, file_bytes)

        return {"filename": filename, "row_count": row_count, "headers": headers}

    async def pop(self, *, tenant_id: str, upload_id: str) -> tuple[str, bytes] | None:
        """Lê e apaga — uso único, a Tool nunca reaproveita o mesmo upload duas vezes."""

        key = self._redis_key(tenant_id, upload_id)
        stored = await self._read(tenant_id, upload_id)
        if stored is not None:
            await self._redis.delete(key)
        return stored

    async def _read(self, tenant_id: str, upload_id: str) -> tuple[str, bytes] | None:
        raw = await self._redis.get(self._redis_key(tenant_id, upload_id))
        if raw is None:
            return None
        parsed = json.loads(raw)
        return parsed["filename"], base64.b64decode(parsed["data"])

    @staticmethod
    def _redis_key(tenant_id: str, upload_id: str) -> str:
        return f"ai_upload:{tenant_id}:{upload_id}"


def get_ai_upload_store() -> AiUploadStore:
    return AiUploadStore(get_redis_client())
