"""Controller do AI Gateway. Nenhuma regra de negócio aqui — apenas delega ao provider
selecionado pela fábrica, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

import httpx
from fastapi import APIRouter
from veloai_shared.exceptions import AppException
from veloai_shared.responses import SuccessResponse

from app.core.config import get_settings
from app.providers.factory import get_provider
from app.schemas.generate import GenerateRequest, GenerateResponse

router = APIRouter(tags=["ai"])


@router.post("/generate")
async def generate(payload: GenerateRequest) -> SuccessResponse[GenerateResponse]:
    settings = get_settings()
    provider = get_provider(settings)

    try:
        result = await provider.generate(payload.prompt, system_prompt=payload.system_prompt)
    except httpx.HTTPError as exc:
        raise AppException(
            "Falha ao consultar o provedor de IA.",
            code="AI_PROVIDER_ERROR",
            status_code=502,
        ) from exc

    return SuccessResponse(
        message="Resposta gerada com sucesso.",
        data=GenerateResponse(
            text=result.text,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
        ),
    )


@router.get("/models")
async def list_models() -> SuccessResponse[list[str]]:
    settings = get_settings()
    provider = get_provider(settings)
    models = await provider.list_models()
    return SuccessResponse(message="Modelos disponíveis.", data=models)
