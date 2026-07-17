"""DTOs do endpoint `/embeddings` (RAG — Fase 15)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EmbeddingsRequest(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=100)


class EmbeddingsResponse(BaseModel):
    embeddings: list[list[float]]
    model: str
