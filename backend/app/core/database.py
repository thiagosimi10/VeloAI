"""Conexão ao Banco Master e Gerenciador de Conexões por Tenant, conforme
04-MULTI-TENANCY.md ("Conexão Dinâmica: Login → Banco Master → Localiza Tenant → Obtém
configuração → Cria conexão SQLAlchemy → Armazena Pool → Requisições utilizam conexão
correta") e 16-BACKEND-ARCHITECTURE.md ("Connection Manager").

O Backend autentica exclusivamente como a role `veloai_app` — nunca cria bancos, nunca
executa DDL. Toda operação administrativa é responsabilidade do Provisioning Service."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from veloai_shared.schema.master import Tenant, TenantUserIndex

from app.core.config import get_settings


@lru_cache
def get_master_engine() -> AsyncEngine:
    """Engine com pool reutilizável para o Banco Master, usando a role `veloai_app`."""

    settings = get_settings()
    return create_async_engine(settings.master_database_url, pool_pre_ping=True)


def get_master_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=get_master_engine(), expire_on_commit=False)


@asynccontextmanager
async def get_master_session() -> AsyncIterator[AsyncSession]:
    session_factory = get_master_sessionmaker()
    async with session_factory() as session:
        yield session


class TenantConnectionManager:
    """Resolve o Tenant de um usuário a partir do Banco Master e mantém um pool de
    conexões cacheado por tenant — nunca cria uma conexão nova a cada requisição."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._engines: dict[uuid.UUID, AsyncEngine] = {}

    async def resolve_tenant_by_email(self, email: str) -> Tenant | None:
        """Primeiro passo do fluxo de login: descobre a qual tenant um e-mail pertence
        através do índice de roteamento (`tenant_user_index`) do Banco Master."""

        async with get_master_session() as session:
            index_result = await session.execute(
                select(TenantUserIndex.tenant_id).where(TenantUserIndex.email == email)
            )
            tenant_id = index_result.scalar_one_or_none()
            if tenant_id is None:
                return None
            return await session.get(Tenant, tenant_id)

    async def get_tenant_by_id(self, tenant_id: uuid.UUID) -> Tenant | None:
        """Usado quando só se tem o `tenant_id` das claims do JWT (ex.: `GET /auth/me`)
        e é preciso exibir dados do tenant (nome) que só existem no Banco Master."""

        async with get_master_session() as session:
            return await session.get(Tenant, tenant_id)

    @asynccontextmanager
    async def session_for_tenant(
        self, tenant_id: uuid.UUID, database_name: str
    ) -> AsyncIterator[AsyncSession]:
        """Abre uma sessão no banco exclusivo do tenant, reutilizando o pool já aberto
        quando existir. Recebe `tenant_id`/`database_name` como primitivos (em vez de um
        `Tenant` completo) para que possa ser chamado tanto após a resolução por e-mail
        (login) quanto a partir das claims já embutidas no JWT (demais requisições),
        sem exigir uma nova consulta ao Banco Master a cada requisição autenticada."""

        engine = self._get_or_create_engine(tenant_id, database_name)
        session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
        async with session_factory() as session:
            yield session

    def _get_or_create_engine(self, tenant_id: uuid.UUID, database_name: str) -> AsyncEngine:
        engine = self._engines.get(tenant_id)
        if engine is None:
            url = self._settings.tenant_database_url(database_name)
            engine = create_async_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5)
            self._engines[tenant_id] = engine
        return engine

    async def dispose_all(self) -> None:
        for engine in self._engines.values():
            await engine.dispose()
        self._engines.clear()


@lru_cache
def get_tenant_connection_manager() -> TenantConnectionManager:
    return TenantConnectionManager()


async def dispose_engines() -> None:
    """Fecha todos os pools de conexão. Chamado no shutdown da aplicação e ao final dos
    testes de integração."""

    await get_master_engine().dispose()
    await get_tenant_connection_manager().dispose_all()
