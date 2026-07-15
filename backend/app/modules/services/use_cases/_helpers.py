"""Utilitário interno compartilhado entre os use cases de Serviços."""

from __future__ import annotations

from typing import Any

from veloai_shared.schema.tenant import Service

from app.modules.services.schemas.service import ServiceResponse


def serialize_service(service: Service) -> dict[str, Any]:
    """Serializa um `Service` para um dict JSON-safe (UUID/datetime/Decimal como
    string), usado para popular `before`/`after` da auditoria."""

    return ServiceResponse.model_validate(service).model_dump(mode="json")
