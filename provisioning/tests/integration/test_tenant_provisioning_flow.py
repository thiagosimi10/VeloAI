"""Teste de ponta a ponta: cria um Tenant de verdade (banco PostgreSQL exclusivo,
migrations, seed e usuário administrador) e depois desfaz tudo."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from veloai_shared.exceptions import ConflictError
from veloai_shared.permissions_catalog import DEFAULT_ADMIN_PERMISSIONS
from veloai_shared.schema.master import Tenant, TenantStatus, TenantUserIndex
from veloai_shared.schema.tenant import (
    TenantPermission,
    TenantRole,
    TenantRolePermission,
    TenantUser,
)

from app.core.config import get_settings
from app.core.database import get_master_session
from app.schemas.tenant import CreateTenantRequest
from app.services.database_admin_service import DatabaseAdminService
from app.services.tenant_provisioning_service import TenantProvisioningService

from .conftest import APP_ROLE_TEST_PASSWORD


async def test_provision_creates_real_database_with_admin_user(master_database: None) -> None:
    service = TenantProvisioningService()
    payload = CreateTenantRequest(
        legal_name="Assistência Técnica Silva LTDA",
        trade_name="Assistência Silva",
        document="12345678000199",
        admin_name="Maria Souza",
        admin_email="maria@assistenciasilva.test",
    )

    result = await service.provision(payload)
    try:
        assert result.status == TenantStatus.ACTIVE.value
        assert result.database_name.startswith("tenant_")
        assert result.admin.admin_email == "maria@assistenciasilva.test"
        assert len(result.admin.temporary_password) > 0

        async with get_master_session() as session:
            master_row = await session.get(Tenant, result.tenant_id)
            assert master_row is not None
            assert master_row.status == TenantStatus.ACTIVE.value
            assert master_row.database_name == result.database_name

            index_result = await session.execute(
                select(TenantUserIndex).where(
                    TenantUserIndex.email == "maria@assistenciasilva.test"
                )
            )
            index_entry = index_result.scalar_one()
            assert index_entry.tenant_id == result.tenant_id

        settings = get_settings()
        tenant_engine = create_async_engine(settings.tenant_database_url(result.database_name))
        try:
            async with tenant_engine.connect() as connection:
                async with AsyncSession(bind=connection) as tenant_session:
                    admin_result = await tenant_session.execute(
                        select(TenantUser).where(
                            TenantUser.email == "maria@assistenciasilva.test"
                        )
                    )
                    admin_user = admin_result.scalar_one()
                    assert admin_user.force_password_change is True
                    assert admin_user.password_hash != result.admin.temporary_password

                    permissions_result = await tenant_session.execute(
                        select(TenantPermission.module, TenantPermission.action)
                        .join(
                            TenantRolePermission,
                            TenantRolePermission.permission_id == TenantPermission.id,
                        )
                        .join(TenantRole, TenantRole.id == TenantRolePermission.role_id)
                        .where(TenantRole.name == "Administrador")
                    )
                    granted = {f"{module}.{action}" for module, action in permissions_result.all()}
                    expected = {f"{module}.{action}" for module, action in DEFAULT_ADMIN_PERMISSIONS}
                    assert granted == expected
        finally:
            await tenant_engine.dispose()

        # A role `veloai_app` (usada pelo Backend) deve conseguir ler a tabela `users`
        # do tenant recém-criado — valida que o GRANT de privilégios funcionou.
        app_role_url = (
            f"postgresql+asyncpg://{settings.postgres_app_user}:{APP_ROLE_TEST_PASSWORD}"
            f"@{settings.postgres_host}:{settings.postgres_port}/{result.database_name}"
        )
        app_role_engine = create_async_engine(app_role_url)
        try:
            async with app_role_engine.connect() as connection:
                async with AsyncSession(bind=connection) as app_role_session:
                    app_role_result = await app_role_session.execute(
                        select(TenantUser).where(
                            TenantUser.email == "maria@assistenciasilva.test"
                        )
                    )
                    assert app_role_result.scalar_one().email == "maria@assistenciasilva.test"
        finally:
            await app_role_engine.dispose()
    finally:
        await DatabaseAdminService().drop_database(result.database_name)


async def test_provision_rejects_duplicate_document(master_database: None) -> None:
    service = TenantProvisioningService()
    payload = CreateTenantRequest(
        legal_name="Empresa Duplicada LTDA",
        document="98765432000188",
        admin_name="Carlos Lima",
        admin_email="carlos@duplicada.test",
    )

    result = await service.provision(payload)
    try:
        duplicate_payload = payload.model_copy(update={"admin_email": "outro@duplicada.test"})
        try:
            await service.provision(duplicate_payload)
            raise AssertionError("Deveria ter levantado ConflictError para documento duplicado.")
        except ConflictError as exc:
            assert exc.code == "TENANT_ALREADY_EXISTS"
    finally:
        await DatabaseAdminService().drop_database(result.database_name)
