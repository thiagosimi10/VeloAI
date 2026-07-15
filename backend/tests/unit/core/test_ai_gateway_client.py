from decimal import Decimal

import httpx
import pytest
import respx
from veloai_shared.exceptions import AppException

from app.core.ai_gateway_client import AIGatewayClient

_BASE_URL = "http://ai-gateway.test:8002"


@respx.mock
async def test_generate_parses_successful_envelope() -> None:
    respx.post(f"{_BASE_URL}/generate").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": True,
                "message": "Resposta gerada com sucesso.",
                "data": {
                    "text": "Você vendeu R$ 12.340,00 em maio.",
                    "model": "gemini-3.1-flash-lite",
                    "input_tokens": 40,
                    "output_tokens": 20,
                    "cached": False,
                    "estimated_cost": "0.0000120",
                },
            },
        )
    )
    client = AIGatewayClient(base_url=_BASE_URL)

    result = await client.generate("Quanto vendi em maio?", system_prompt="Contexto de teste.")

    assert result.text == "Você vendeu R$ 12.340,00 em maio."
    assert result.model == "gemini-3.1-flash-lite"
    assert result.input_tokens == 40
    assert result.output_tokens == 20
    assert result.cached is False
    assert result.estimated_cost == Decimal("0.0000120")


@respx.mock
async def test_generate_raises_app_exception_on_network_error() -> None:
    respx.post(f"{_BASE_URL}/generate").mock(return_value=httpx.Response(502))
    client = AIGatewayClient(base_url=_BASE_URL)

    with pytest.raises(AppException) as exc_info:
        await client.generate("Quanto vendi em maio?")

    assert exc_info.value.code == "AI_GATEWAY_ERROR"
    assert exc_info.value.status_code == 502
