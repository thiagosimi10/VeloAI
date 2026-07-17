"""DTOs do módulo de Base de Conhecimento (RAG — Fase 15), conforme docs/21-RAG.md.
Texto puro (título + conteúdo) — sem upload de arquivo/OCR nesta fase (ver
`app/modules/README.md`)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CreateKnowledgeDocumentRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=1)


class KnowledgeDocumentResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeDocumentFilterParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class KnowledgeSearchResult(BaseModel):
    title: str
    content: str
    score: float
