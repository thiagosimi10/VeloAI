"""Envelope padrão de respostas da API, conforme 22-API-STANDARDS.md."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Metadados de paginação retornados em `meta` quando a resposta é uma lista."""

    model_config = ConfigDict(frozen=True)

    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)
    pages: int = Field(ge=0)


class SuccessResponse(BaseModel, Generic[T]):
    """Formato obrigatório para toda resposta de sucesso da API."""

    success: bool = True
    message: str
    data: T
    meta: dict[str, Any] | PaginationMeta | None = None


class ErrorResponse(BaseModel):
    """Formato obrigatório para toda resposta de erro da API. Nunca inclui traceback."""

    success: bool = False
    message: str
    code: str
    errors: list[dict[str, Any]] = Field(default_factory=list)
    trace_id: str
