"""Utilitário interno compartilhado entre os use cases de Produtos."""

from __future__ import annotations

from typing import Any

from veloai_shared.schema.tenant import Product

from app.modules.products.schemas.product import ProductResponse


def serialize_product(product: Product) -> dict[str, Any]:
    """Serializa um `Product` para um dict JSON-safe (UUID/datetime/Decimal como
    string), usado para popular `before`/`after` da auditoria."""

    return ProductResponse.model_validate(product).model_dump(mode="json")
