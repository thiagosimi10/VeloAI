"""Controller do AI Gateway. Nenhuma regra de negócio aqui — apenas delega ao provider
selecionado pela fábrica, conforme 00-AI-CONSTITUTION.md."""

from __future__ import annotations

import httpx
from fastapi import APIRouter
from redis.exceptions import RedisError
from veloai_shared.exceptions import AppException
from veloai_shared.responses import SuccessResponse

from app.core.cache import (
    build_cache_key,
    get_cached_response,
    get_redis_client,
    set_cached_response,
)
from app.core.config import get_settings
from app.providers.base import ToolDeclaration
from app.providers.factory import get_provider
from app.schemas.embeddings import EmbeddingsRequest, EmbeddingsResponse
from app.schemas.generate import FunctionCallDTO, GenerateRequest, GenerateResponse

router = APIRouter(tags=["ai"])


@router.post("/generate")
async def generate(payload: GenerateRequest) -> SuccessResponse[GenerateResponse]:
    settings = get_settings()
    provider = get_provider(settings)
    redis_client = get_redis_client()

    tools = (
        [
            ToolDeclaration(
                name=tool.name, description=tool.description, parameters=tool.parameters
            )
            for tool in payload.tools
        ]
        if payload.tools
        else None
    )
    cache_key = build_cache_key(
        settings.ai_report_model, payload.system_prompt, payload.prompt, tools
    )

    # O cache é um atalho, nunca uma dependência dura: se o Redis estiver fora do ar,
    # degrada para "sempre miss" e o /generate continua funcionando normalmente.
    try:
        cached_result = await get_cached_response(redis_client, cache_key)
    except RedisError:
        cached_result = None

    cached = cached_result is not None
    if cached_result is not None:
        result = cached_result
    else:
        try:
            result = await provider.generate(
                payload.prompt, system_prompt=payload.system_prompt, tools=tools
            )
        except httpx.HTTPError as exc:
            raise AppException(
                "Falha ao consultar o provedor de IA.",
                code="AI_PROVIDER_ERROR",
                status_code=502,
            ) from exc

        try:
            await set_cached_response(
                redis_client, cache_key, result, ttl_seconds=settings.ai_cache_ttl_seconds
            )
        except RedisError:
            pass

    result_function_call = result.function_call
    function_call = (
        FunctionCallDTO(name=result_function_call.name, arguments=result_function_call.arguments)
        if result_function_call is not None
        else None
    )

    return SuccessResponse(
        message="Resposta gerada com sucesso.",
        data=GenerateResponse(
            text=result.text,
            function_call=function_call,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cached=cached,
            estimated_cost=provider.estimate_cost(result.input_tokens, result.output_tokens),
        ),
    )


@router.get("/models")
async def list_models() -> SuccessResponse[list[str]]:
    settings = get_settings()
    provider = get_provider(settings)
    models = await provider.list_models()
    return SuccessResponse(message="Modelos disponíveis.", data=models)


@router.post("/embeddings")
async def embeddings(payload: EmbeddingsRequest) -> SuccessResponse[EmbeddingsResponse]:
    settings = get_settings()
    provider = get_provider(settings)

    try:
        vectors = await provider.embeddings(payload.texts)
    except httpx.HTTPError as exc:
        raise AppException(
            "Falha ao consultar o provedor de IA.",
            code="AI_PROVIDER_ERROR",
            status_code=502,
        ) from exc

    return SuccessResponse(
        message="Embeddings gerados com sucesso.",
        data=EmbeddingsResponse(embeddings=vectors, model=settings.ai_embedding_model),
    )
