"""DTOs do módulo de IA, conforme 22-API-STANDARDS.md e 05-BANCO-DE-DADOS.md (tabela
`ai_conversations`)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AskAIRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)


class AskAIResponse(BaseModel):
    response: str
    model: str
    tokens: int
    execution_time: Decimal
    cached: bool
    estimated_cost: Decimal
    tool_used: str | None = None


class AiConversationResponse(BaseModel):
    id: uuid.UUID
    prompt: str
    response: str
    tokens: int
    model: str
    execution_time: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class AiConversationFilterParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
