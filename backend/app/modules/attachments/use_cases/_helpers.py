"""Validação de existência do recurso alvo de um anexo, reaproveitando os Use Cases já
existentes de cada módulo (nunca seus `repositories` diretamente, conforme
`app/modules/README.md`). Restrita aos três tipos de recurso suportados nesta fase —
ver `app/modules/README.md` e `schemas/attachment.py`."""

from __future__ import annotations

import uuid

from app.core.database import TenantConnectionManager
from app.modules.attachments.schemas.attachment import AttachmentResourceType
from app.modules.customers.use_cases.get_customer_use_case import GetCustomerUseCase
from app.modules.products.use_cases.get_product_use_case import GetProductUseCase
from app.modules.service_orders.use_cases.get_service_order_use_case import (
    GetServiceOrderUseCase,
)


async def ensure_resource_exists(
    *,
    connection_manager: TenantConnectionManager,
    resource_type: AttachmentResourceType,
    resource_id: uuid.UUID,
    tenant_id: uuid.UUID,
    database_name: str,
) -> None:
    if resource_type == "customer":
        await GetCustomerUseCase(connection_manager=connection_manager).execute(
            tenant_id=tenant_id, database_name=database_name, customer_id=resource_id
        )
    elif resource_type == "product":
        await GetProductUseCase(connection_manager=connection_manager).execute(
            tenant_id=tenant_id, database_name=database_name, product_id=resource_id
        )
    elif resource_type == "service_order":
        await GetServiceOrderUseCase(connection_manager=connection_manager).execute(
            tenant_id=tenant_id, database_name=database_name, order_id=resource_id
        )
