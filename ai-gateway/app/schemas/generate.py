"""DTOs do endpoint `/generate`."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    system_prompt: str | None = Field(default=None, max_length=4000)


class GenerateResponse(BaseModel):
    text: str
    model: str
    input_tokens: int
    output_tokens: int
