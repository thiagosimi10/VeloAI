"""Utilitário interno compartilhado entre os use cases de Clientes."""

from __future__ import annotations

from typing import Any

from veloai_shared.schema.tenant import Customer

from app.modules.customers.schemas.customer import CustomerResponse


def serialize_customer(customer: Customer) -> dict[str, Any]:
    """Serializa um `Customer` para um dict JSON-safe (UUID/datetime como string),
    usado para popular `before`/`after` da auditoria."""

    return CustomerResponse.model_validate(customer).model_dump(mode="json")
