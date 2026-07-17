"""Convenção de nome de Collection do Qdrant, conforme 04-MULTI-TENANCY.md ("Cada
empresa possuirá sua própria Collection", formato `tenant_{uuid}_vectors"). Único
lugar onde esse formato é definido — Provisioning (cria a Collection) e Backend
(indexa/busca nela) importam esta função para nunca divergir."""

from __future__ import annotations

import uuid


def collection_name_for_tenant(tenant_id: uuid.UUID) -> str:
    return f"tenant_{tenant_id}_vectors"
