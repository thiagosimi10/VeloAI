"""CLI: aplica as migrations pendentes de `alembic_tenant` em TODOS os bancos de tenant
já provisionados.

Necessário sempre que uma migration nova é adicionada depois que tenants já existem —
tenants criados a partir de então já recebem a migration automaticamente durante o
provisionamento (`TenantProvisioningService.provision`), mas os que já existiam antes
da migration nova ficam parados na revisão anterior até este script rodar.

Uso:
    python -m scripts.migrate_all_tenants
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select
from veloai_shared.schema.master import Tenant

from app.core.database import get_master_session
from app.core.logging import configure_logging, get_logger
from app.services.database_admin_service import DatabaseAdminService

configure_logging(service_name="provisioning-migrate-tenants")
logger = get_logger(__name__)


async def _list_tenant_database_names() -> list[str]:
    async with get_master_session() as session:
        result = await session.execute(select(Tenant.database_name))
        return list(result.scalars().all())


def main() -> None:
    database_names = asyncio.run(_list_tenant_database_names())
    logger.info("migrate_all_tenants_started", tenant_count=len(database_names))

    admin_service = DatabaseAdminService()
    failed: list[str] = []
    for database_name in database_names:
        logger.info("migrate_tenant_started", database_name=database_name)
        try:
            admin_service.run_tenant_migrations(database_name)
        except Exception:  # noqa: BLE001 - um tenant com banco quebrado nunca pode
            # impedir o boot do serviço nem a migration dos demais tenants.
            logger.exception("migrate_tenant_failed", database_name=database_name)
            failed.append(database_name)
        else:
            logger.info("migrate_tenant_finished", database_name=database_name)

    logger.info("migrate_all_tenants_finished", failed_count=len(failed), failed=failed)


if __name__ == "__main__":
    main()
