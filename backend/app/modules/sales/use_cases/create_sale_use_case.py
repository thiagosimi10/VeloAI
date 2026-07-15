"""Caso de uso: criar Venda. Garante que `customer_id` exista — reaproveitando
`GetCustomerUseCase` (nunca acessando o repository de outro módulo diretamente,
conforme `app/modules/README.md`)."""

from __future__ import annotations

import uuid

from veloai_shared.schema.tenant import Sale

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.customers.use_cases.get_customer_use_case import GetCustomerUseCase
from app.modules.sales.repositories.sale_repository import SaleRepository
from app.modules.sales.schemas.sale import CreateSaleRequest, SaleResponse
from app.modules.sales.use_cases._helpers import serialize_sale, to_response


class CreateSaleUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payload: CreateSaleRequest,
    ) -> SaleResponse:
        await GetCustomerUseCase(connection_manager=self._connections).execute(
            tenant_id=tenant_id, database_name=database_name, customer_id=payload.customer_id
        )

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = SaleRepository(session)

            sale = Sale(customer_id=payload.customer_id, payment_method=payload.payment_method)
            await repository.create(sale)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="SALE_CREATED",
                resource="sales",
                after=serialize_sale(sale),
            )
            await session.commit()

            return to_response(sale)
