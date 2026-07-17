"""'Prompt Builder' enxuto do módulo de IA: monta um system prompt fixo com contexto de
empresa/usuário antes de repassar ao AI Gateway. Sem versionamento, sem camadas
System/Developer/Context/Memory separadas — isso é uma fase futura (Prompt Builder
completo, ver docs/13-IA-PLATFORM.md)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import Company


async def get_company_display_name(session: AsyncSession) -> str:
    result = await session.execute(select(Company))
    company = result.scalars().first()
    if company is None:
        return "a empresa"
    return company.trade_name or company.legal_name


def build_system_prompt(*, company_name: str, user_name: str, role: str) -> str:
    today = datetime.now(UTC).strftime("%d/%m/%Y")
    return (
        f"Você é o assistente de IA do VeloAI, integrado ao sistema da empresa "
        f"{company_name}. Você está respondendo a {user_name}, cujo papel é '{role}' "
        f"nesta empresa. A data de hoje é {today}. Responda sempre em português do "
        f"Brasil, de forma clara, objetiva e profissional. Quando uma ferramenta "
        f"disponível puder executar o que o usuário pediu, use-a em vez de apenas "
        f"descrever como fazer."
    )
