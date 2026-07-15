"""Utilitário interno compartilhado entre os use cases de Fornecedores."""

from __future__ import annotations

from typing import Any

from veloai_shared.schema.tenant import Supplier

from app.modules.suppliers.schemas.supplier import SupplierResponse


def serialize_supplier(supplier: Supplier) -> dict[str, Any]:
    """Serializa um `Supplier` para um dict JSON-safe (UUID/datetime como string),
    usado para popular `before`/`after` da auditoria."""

    return SupplierResponse.model_validate(supplier).model_dump(mode="json")
