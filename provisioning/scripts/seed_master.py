"""CLI: garante a existência do plano inicial e do primeiro operador da plataforma no
Banco Master, conforme 31-BILLING.md ("Plano Inicial: VeloAI Professional, R$ 129,90 /
mês, Trial de 14 dias") e 34-MASTER-PLAN.md (Fase 18, "Admin Master").

Uso:
    python -m scripts.seed_master

Idempotente — pode ser executado múltiplas vezes sem duplicar o plano/admin.
"""

from __future__ import annotations

import asyncio
import os
from decimal import Decimal

from sqlalchemy import select
from veloai_shared.schema.master import Plan, PlatformAdmin
from veloai_shared.security import hash_password

from app.core.database import get_master_session
from app.core.logging import configure_logging, get_logger

configure_logging(service_name="provisioning-seed-master")
logger = get_logger(__name__)

DEFAULT_PLAN_NAME = "VeloAI Professional"
DEFAULT_PLAN_PRICE = Decimal("129.90")
DEFAULT_TRIAL_DAYS = 14


async def seed_default_plan() -> None:
    async with get_master_session() as session:
        result = await session.execute(select(Plan).where(Plan.name == DEFAULT_PLAN_NAME))
        existing_plan = result.scalar_one_or_none()

        if existing_plan is not None:
            logger.info("seed_master_skipped_plan_exists", plan=DEFAULT_PLAN_NAME)
            return

        session.add(
            Plan(
                name=DEFAULT_PLAN_NAME,
                price=DEFAULT_PLAN_PRICE,
                trial_days=DEFAULT_TRIAL_DAYS,
                active=True,
            )
        )
        await session.commit()
        logger.info("seed_master_plan_created", plan=DEFAULT_PLAN_NAME)


async def seed_platform_admin() -> None:
    """Cria o primeiro operador da plataforma a partir de `PLATFORM_ADMIN_EMAIL`/
    `PLATFORM_ADMIN_PASSWORD` — sem esses dois valores, não há como saber qual e-mail/
    senha usar, então a etapa é pulada (nunca falha o boot do container por isso)."""

    email = os.environ.get("PLATFORM_ADMIN_EMAIL")
    password = os.environ.get("PLATFORM_ADMIN_PASSWORD")
    if not email or not password:
        logger.warning("seed_master_skipped_platform_admin_env_missing")
        return

    async with get_master_session() as session:
        result = await session.execute(
            select(PlatformAdmin).where(PlatformAdmin.email == email)
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin is not None:
            logger.info("seed_master_skipped_platform_admin_exists", email=email)
            return

        session.add(
            PlatformAdmin(
                email=email,
                password_hash=hash_password(password),
                first_name="Admin",
                active=True,
                force_password_change=True,
            )
        )
        await session.commit()
        logger.info("seed_master_platform_admin_created", email=email)


async def _seed_all() -> None:
    await seed_default_plan()
    await seed_platform_admin()


def main() -> None:
    asyncio.run(_seed_all())


if __name__ == "__main__":
    main()
