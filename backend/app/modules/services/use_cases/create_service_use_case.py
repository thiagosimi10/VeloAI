"""Caso de uso: criar serviço. Gera o `code` sequencial e garante que `category_id`,
quando informado, aponte para uma categoria existente — reaproveitando `GetCategoryUseCase`
(nunca acessando o repository de outro módulo diretamente, conforme
`app/modules/README.md`)."""

from __future__ import annotations

import uuid

from veloai_shared.schema.tenant import Service

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.categories.use_cases.get_category_use_case import GetCategoryUseCase
from app.modules.services.repositories.service_repository import ServiceRepository
from app.modules.services.schemas.service import CreateServiceRequest, ServiceResponse
from app.modules.services.use_cases._helpers import serialize_service


class CreateServiceUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payload: CreateServiceRequest,
    ) -> ServiceResponse:
        if payload.category_id is not None:
            await GetCategoryUseCase(connection_manager=self._connections).execute(
                tenant_id=tenant_id, database_name=database_name, category_id=payload.category_id
            )

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = ServiceRepository(session)

            sequence = await repository.count_all() + 1
            service = Service(code=f"S{sequence:06d}", **payload.model_dump())
            await repository.create(service)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SERVICE_CREATED",
                resource="services",
                after=serialize_service(service),
            )
            await session.commit()

            return ServiceResponse.model_validate(service)
