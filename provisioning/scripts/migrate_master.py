"""CLI: aplica as migrations do Banco Master (`alembic_master`).

Uso:
    python -m scripts.migrate_master
"""

from __future__ import annotations

import asyncio

from app.core.logging import configure_logging, get_logger
from app.services.database_admin_service import DatabaseAdminService

configure_logging(service_name="provisioning-migrate-master")
logger = get_logger(__name__)


def main() -> None:
    logger.info("migrate_master_started")
    admin_service = DatabaseAdminService()
    admin_service.run_master_migrations()
    asyncio.run(admin_service.grant_app_role_privileges_on_master())
    logger.info("migrate_master_finished")


if __name__ == "__main__":
    main()
