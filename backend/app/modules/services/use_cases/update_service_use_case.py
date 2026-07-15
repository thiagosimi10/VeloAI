"""Caso de uso: atualizar serviço (atualização parcial)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.categories.use_cases.get_category_use_case import GetCategoryUseCase
from app.modules.services.repositories.service_repository import ServiceRepository
from app.modules.services.schemas.service import ServiceResponse, UpdateServiceRequest
from app.modules.services.use_cases._helpers import serialize_service


class UpdateServiceUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        service_id: uuid.UUID,
        payload: UpdateServiceRequest,
    ) -> ServiceResponse:
        if payload.category_id is not None:
            await GetCategoryUseCase(connection_manager=self._connections).execute(
                tenant_id=tenant_id, database_name=database_name, category_id=payload.category_id
            )

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = ServiceRepository(session)
            service = await repository.get_by_id(service_id)
            if service is None:
                raise NotFoundError("Serviço não encontrado.", code="SERVICE_NOT_FOUND")

            before = serialize_service(service)
            update_data = payload.model_dump(exclude_unset=True)
            await repository.update(service, update_data)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SERVICE_UPDATED",
                resource="services",
                before=before,
                after=serialize_service(service),
            )
            await session.commit()

            return ServiceResponse.model_validate(service)
