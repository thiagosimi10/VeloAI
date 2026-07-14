"""Seed inicial de cada novo banco de tenant: empresa, papel Administrador, permissão
mínima e usuário administrador — conforme 19-PROVISIONING-SERVICE.md ("Criar usuário
administrador. Receber nome, email, senha temporária. Obrigar troca no primeiro
login.")."""

from __future__ import annotations

import secrets
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.tenant_template import (
    Company,
    TenantPermission,
    TenantRole,
    TenantRolePermission,
    TenantUser,
)
from veloai_shared.security import hash_password


@dataclass(frozen=True)
class TenantAdminSeed:
    company_id: uuid.UUID
    admin_user_id: uuid.UUID
    admin_email: str
    temporary_password: str


class TenantSeedService:
    """Conecta-se diretamente ao banco recém-criado do tenant (conexão de curta duração,
    descartada ao final) para inserir os dados mínimos necessários para o primeiro
    login."""

    async def seed(
        self,
        *,
        database_name: str,
        legal_name: str,
        trade_name: str | None,
        document: str,
        admin_name: str,
        admin_email: str,
    ) -> TenantAdminSeed:
        settings = get_settings()
        engine = create_async_engine(
            settings.tenant_database_url(database_name), pool_pre_ping=True
        )
        session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
        temporary_password = secrets.token_urlsafe(15)

        try:
            async with session_factory() as session, session.begin():
                company = Company(legal_name=legal_name, trade_name=trade_name, document=document)
                session.add(company)
                await session.flush()

                role = TenantRole(name="Administrador", description="Acesso total ao sistema.")
                session.add(role)
                await session.flush()

                permission = TenantPermission(module="system", action="admin")
                session.add(permission)
                await session.flush()

                session.add(TenantRolePermission(role_id=role.id, permission_id=permission.id))

                first_name, _, last_name = admin_name.strip().partition(" ")
                admin_user = TenantUser(
                    company_id=company.id,
                    role_id=role.id,
                    first_name=first_name or admin_name,
                    last_name=last_name or None,
                    email=admin_email,
                    password_hash=hash_password(temporary_password),
                    force_password_change=True,
                )
                session.add(admin_user)
                await session.flush()

                return TenantAdminSeed(
                    company_id=company.id,
                    admin_user_id=admin_user.id,
                    admin_email=admin_email,
                    temporary_password=temporary_password,
                )
        finally:
            await engine.dispose()
