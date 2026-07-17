"""Orquestra o fluxo completo de provisionamento de um novo Tenant, conforme
19-PROVISIONING-SERVICE.md:

validar → registrar tenant (PROVISIONING) → criar banco → migrations → grant → criar
Collection Qdrant (04-MULTI-TENANCY.md, Fase 15) → seed → criar Assinatura TRIAL
(31-BILLING.md, Fase 17) → registrar tenant (ACTIVE) → auditoria. Qualquer falha marca o
tenant como FAILED e tenta desfazer o banco e a Collection já criados, sem mascarar o
erro original."""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from veloai_shared.exceptions import ConflictError
from veloai_shared.schema.master import Subscription, SubscriptionStatus, Tenant, TenantStatus
from veloai_shared.security import new_uuid7, short_id

from app.core.config import get_settings
from app.core.database import get_master_session
from app.core.logging import get_logger
from app.repositories.tenant_repository import TenantRepository
from app.schemas.tenant import (
    CreateTenantRequest,
    TenantAdminCredentials,
    TenantProvisionedResponse,
)
from app.services.database_admin_service import DatabaseAdminService
from app.services.qdrant_provisioning_service import QdrantProvisioningService
from app.services.seed_service import TenantSeedService

logger = get_logger(__name__)


class TenantProvisioningService:
    def __init__(
        self,
        *,
        database_admin_service: DatabaseAdminService | None = None,
        seed_service: TenantSeedService | None = None,
        qdrant_service: QdrantProvisioningService | None = None,
    ) -> None:
        self._settings = get_settings()
        self._db_admin = database_admin_service or DatabaseAdminService()
        self._seed = seed_service or TenantSeedService()
        self._qdrant = qdrant_service or QdrantProvisioningService()

    async def provision(self, payload: CreateTenantRequest) -> TenantProvisionedResponse:
        async with get_master_session() as session:
            repository = TenantRepository(session)

            existing = await repository.get_by_document(payload.document)
            if existing is not None:
                raise ConflictError(
                    "Já existe uma empresa cadastrada com este documento.",
                    code="TENANT_ALREADY_EXISTS",
                )

            tenant_id = new_uuid7()
            database_name = f"{self._settings.tenant_database_prefix}{short_id(tenant_id)}"

            tenant = Tenant(
                id=tenant_id,
                legal_name=payload.legal_name,
                trade_name=payload.trade_name,
                document=payload.document,
                database_name=database_name,
                database_host=self._settings.postgres_host,
                database_port=self._settings.postgres_port,
                status=TenantStatus.PROVISIONING.value,
            )
            await repository.create(tenant)
            await repository.add_audit_log(
                tenant_id=tenant_id,
                action="TENANT_PROVISIONING_STARTED",
                resource="tenants",
                after={"database_name": database_name},
            )
            await repository.commit()

            try:
                await self._db_admin.create_database(database_name)
                await asyncio.to_thread(self._db_admin.run_tenant_migrations, database_name)
                await self._db_admin.grant_app_role_privileges(database_name)
                await self._qdrant.create_tenant_collection(tenant_id)
                seed_result = await self._seed.seed(
                    database_name=database_name,
                    legal_name=payload.legal_name,
                    trade_name=payload.trade_name,
                    document=payload.document,
                    admin_name=payload.admin_name,
                    admin_email=payload.admin_email,
                )

                plan = await repository.get_active_plan()
                if plan is None:
                    raise RuntimeError(
                        "Nenhum Plano ativo encontrado no Banco Master — "
                        "verifique se 'scripts.seed_master' foi executado."
                    )
                tenant.plan_id = plan.id
                await repository.create_subscription(
                    Subscription(
                        tenant_id=tenant_id,
                        plan_id=plan.id,
                        status=SubscriptionStatus.TRIAL.value,
                        trial_ends_at=datetime.now(UTC) + timedelta(days=plan.trial_days),
                    )
                )
            except Exception as exc:
                await self._try_cleanup_database(database_name)
                await self._try_cleanup_qdrant_collection(tenant_id)
                await repository.update_status(tenant, TenantStatus.FAILED)
                await repository.add_audit_log(
                    tenant_id=tenant_id,
                    action="TENANT_PROVISIONING_FAILED",
                    resource="tenants",
                    after={"error": str(exc)},
                )
                await repository.commit()
                raise

            await repository.update_status(tenant, TenantStatus.ACTIVE)
            await repository.add_user_index(
                email=seed_result.admin_email, tenant_id=tenant_id
            )
            await repository.add_audit_log(
                tenant_id=tenant_id,
                action="TENANT_PROVISIONING_FINISHED",
                resource="tenants",
                after={"status": TenantStatus.ACTIVE.value},
            )
            await repository.commit()

            return TenantProvisionedResponse(
                tenant_id=tenant_id,
                legal_name=tenant.legal_name,
                document=tenant.document,
                database_name=database_name,
                status=TenantStatus.ACTIVE.value,
                admin=TenantAdminCredentials(
                    admin_email=seed_result.admin_email,
                    temporary_password=seed_result.temporary_password,
                ),
            )

    async def get(self, tenant_id: uuid.UUID) -> Tenant | None:
        async with get_master_session() as session:
            repository = TenantRepository(session)
            return await repository.get_by_id(tenant_id)

    async def _try_cleanup_database(self, database_name: str) -> None:
        try:
            await self._db_admin.drop_database(database_name)
        except Exception:  # noqa: BLE001 - limpeza best-effort, nunca mascara o erro original
            logger.warning("tenant_cleanup_failed", database_name=database_name)

    async def _try_cleanup_qdrant_collection(self, tenant_id: uuid.UUID) -> None:
        try:
            await self._qdrant.delete_tenant_collection(tenant_id)
        except Exception:  # noqa: BLE001 - limpeza best-effort, nunca mascara o erro original
            logger.warning("tenant_qdrant_cleanup_failed", tenant_id=str(tenant_id))
