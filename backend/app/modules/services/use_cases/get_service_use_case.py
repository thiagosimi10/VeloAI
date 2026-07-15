"""Caso de uso: buscar um serviço pelo id."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import TenantConnectionManager
from app.modules.services.repositories.service_repository import ServiceRepository
from app.modules.services.schemas.service import ServiceResponse


class GetServiceUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, service_id: uuid.UUID
    ) -> ServiceResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            service = await ServiceRepository(session).get_by_id(service_id)
            if service is None:
                raise NotFoundError("Serviço não encontrado.", code="SERVICE_NOT_FOUND")
            return ServiceResponse.model_validate(service)
