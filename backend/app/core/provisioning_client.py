"""Cliente HTTP para o Provisioning Service — único ponto por onde o Backend delega
operações administrativas de banco (criação de tenant), conforme `app/core/config.py`
("O Backend nunca possui credenciais administrativas de banco"). Mesmo padrão de
`app/core/ai_gateway_client.py`."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import httpx
from veloai_shared.exceptions import AppException

from app.core.config import get_settings


class ProvisioningClient:
    def __init__(self, *, base_url: str, timeout_seconds: float = 30.0) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    async def create_tenant(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(f"{self._base_url}/tenants", json=payload)
        except httpx.HTTPError as exc:
            raise AppException(
                "Falha ao comunicar com o Provisioning Service. Tente novamente em instantes.",
                code="PROVISIONING_SERVICE_ERROR",
                status_code=502,
            ) from exc

        body = response.json()
        if response.status_code >= 400:
            raise AppException(
                body.get("message", "Falha ao provisionar a empresa."),
                code=body.get("code", "PROVISIONING_SERVICE_ERROR"),
                status_code=response.status_code,
            )
        return body["data"]


@lru_cache
def get_provisioning_client() -> ProvisioningClient:
    """Retorna a instância única (cacheada) de `ProvisioningClient`, mesmo padrão de
    `get_settings()`/`get_ai_gateway_client()`."""

    settings = get_settings()
    return ProvisioningClient(base_url=settings.provisioning_url)
