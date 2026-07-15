"""Utilitário interno compartilhado entre os use cases de Categorias."""

from __future__ import annotations

from typing import Any

from veloai_shared.schema.tenant import Category

from app.modules.categories.schemas.category import CategoryResponse


def serialize_category(category: Category) -> dict[str, Any]:
    """Serializa uma `Category` para um dict JSON-safe (UUID/datetime como string),
    usado para popular `before`/`after` da auditoria."""

    return CategoryResponse.model_validate(category).model_dump(mode="json")
