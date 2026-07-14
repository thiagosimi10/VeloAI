"""CLI: garante a existência do plano inicial no Banco Master, conforme
31-BILLING.md ("Plano Inicial: VeloAI Professional, R$ 129,90 / mês, Trial de 14 dias").

Uso:
    python -m scripts.seed_master

Idempotente — pode ser executado múltiplas vezes sem duplicar o plano.
"""

from __future__ import annotations

import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.core.database import get_master_session
from app.core.logging import configure_logging, get_logger
from app.models.master import Plan

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


def main() -> None:
    asyncio.run(seed_default_plan())


if __name__ == "__main__":
    main()
