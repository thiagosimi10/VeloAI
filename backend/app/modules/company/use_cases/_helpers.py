"""Utilitário interno compartilhado entre os use cases de Configurações da Empresa."""

from __future__ import annotations

from typing import Any

from veloai_shared.schema.tenant import Company

from app.modules.company.schemas.company import CompanyResponse


def serialize_company(company: Company) -> dict[str, Any]:
    """Serializa uma `Company` para um dict JSON-safe (UUID/datetime como string),
    usado para popular `before`/`after` da auditoria."""

    return CompanyResponse.model_validate(company).model_dump(mode="json")
