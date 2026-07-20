"""Caso de uso: criar uma nova empresa (tenant) a partir do Painel Administrativo. O
Backend nunca cria bancos — delega ao Provisioning Service (`app/core/
provisioning_client.py`), que tem as credenciais administrativas necessárias."""

from __future__ import annotations

from app.core.provisioning_client import ProvisioningClient, get_provisioning_client
from app.modules.admin.schemas.admin import (
    CreateTenantRequest,
    TenantAdminCredentials,
    TenantProvisionedResponse,
)


class CreateTenantUseCase:
    def __init__(self, *, provisioning_client: ProvisioningClient | None = None) -> None:
        self._provisioning = provisioning_client or get_provisioning_client()

    async def execute(self, payload: CreateTenantRequest) -> TenantProvisionedResponse:
        data = await self._provisioning.create_tenant(
            {
                "legal_name": payload.legal_name,
                "trade_name": payload.trade_name,
                "document": payload.document,
                "admin_name": payload.admin_name,
                "admin_email": payload.admin_email,
            }
        )

        return TenantProvisionedResponse(
            tenant_id=data["tenant_id"],
            legal_name=data["legal_name"],
            document=data["document"],
            database_name=data["database_name"],
            status=data["status"],
            admin=TenantAdminCredentials(
                admin_email=data["admin"]["admin_email"],
                temporary_password=data["admin"]["temporary_password"],
            ),
        )
