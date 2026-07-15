"""Caso de uso: excluir serviço (soft delete — nunca exclusão física, conforme
00-AI-CONSTITUTION.md)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.services.repositories.service_repository import ServiceRepository
from app.modules.services.use_cases._helpers import serialize_service


class DeleteServiceUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        service_id: uuid.UUID,
    ) -> None:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = ServiceRepository(session)
            service = await repository.get_by_id(service_id)
            if service is None:
                raise NotFoundError("Serviço não encontrado.", code="SERVICE_NOT_FOUND")

            before = serialize_service(service)
            await repository.soft_delete(service)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SERVICE_DELETED",
                resource="services",
                before=before,
            )
            await session.commit()
