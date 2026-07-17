"""DTOs do endpoint `/generate`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class ToolDeclarationDTO(BaseModel):
    """Espelha `app.providers.base.ToolDeclaration` como DTO de entrada — conforme
    docs/20-MCP-TOOLS.md ("Estrutura de uma Tool")."""

    name: str
    description: str
    parameters: dict[str, Any]


class FunctionCallDTO(BaseModel):
    name: str
    arguments: dict[str, Any]


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    system_prompt: str | None = Field(default=None, max_length=4000)
    tools: list[ToolDeclarationDTO] | None = Field(default=None)


class GenerateResponse(BaseModel):
    text: str | None
    function_call: FunctionCallDTO | None = None
    model: str
    input_tokens: int
    output_tokens: int
    cached: bool
    estimated_cost: Decimal
