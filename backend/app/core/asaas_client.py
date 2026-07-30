"""Cliente HTTP para a Asaas — único ponto por onde o Backend fala com o gateway de
pagamento, conforme 31-BILLING.md ("Gateway de Pagamento: Inicialmente Asaas"). Usa o
Checkout hospedado da Asaas (nunca recebemos dado de cartão diretamente — fora do
escopo de PCI compliance do nosso lado), mesmo padrão de `ai_gateway_client.py`/
`provisioning_client.py`."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import httpx
from veloai_shared.exceptions import AppException

from app.core.config import get_settings

# PNG transparente 1x1 — a Asaas exige `items[].imageBase64` em `POST /checkouts`,
# mesmo para produtos digitais sem imagem real.
_PLACEHOLDER_ITEM_IMAGE_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class AsaasClient:
    def __init__(self, *, base_url: str, api_key: str, timeout_seconds: float = 30.0) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    async def create_checkout(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    f"{self._base_url}/checkouts",
                    json=payload,
                    headers={"access_token": self._api_key},
                )
        except httpx.HTTPError as exc:
            raise AppException(
                "Falha ao comunicar com o gateway de pagamento. Tente novamente em instantes.",
                code="ASAAS_ERROR",
                status_code=502,
            ) from exc

        body = response.json()
        if response.status_code >= 400:
            errors = body.get("errors") or []
            message = errors[0]["description"] if errors else "Falha ao criar o checkout."
            raise AppException(message, code="ASAAS_ERROR", status_code=502)
        return body

    @staticmethod
    def placeholder_item_image() -> str:
        return _PLACEHOLDER_ITEM_IMAGE_BASE64


@lru_cache
def get_asaas_client() -> AsaasClient:
    """Retorna a instância única (cacheada) de `AsaasClient`, mesmo padrão de
    `get_settings()`/`get_provisioning_client()`."""

    settings = get_settings()
    return AsaasClient(base_url=settings.asaas_base_url, api_key=settings.asaas_api_key)
