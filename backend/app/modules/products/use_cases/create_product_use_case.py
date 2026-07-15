"""Caso de uso: criar produto. Garante SKU/código de barras únicos e que
`category_id`/`supplier_id`, quando informados, apontem para registros existentes —
reaproveitando os use cases de Categorias/Fornecedores (nunca acessando o repository de
outro módulo diretamente, conforme `app/modules/README.md`)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import ConflictError
from veloai_shared.schema.tenant import Product

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.categories.use_cases.get_category_use_case import GetCategoryUseCase
from app.modules.products.repositories.product_repository import ProductRepository
from app.modules.products.schemas.product import CreateProductRequest, ProductResponse
from app.modules.products.use_cases._helpers import serialize_product
from app.modules.suppliers.use_cases.get_supplier_use_case import GetSupplierUseCase


class CreateProductUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        payload: CreateProductRequest,
    ) -> ProductResponse:
        if payload.category_id is not None:
            await GetCategoryUseCase(connection_manager=self._connections).execute(
                tenant_id=tenant_id, database_name=database_name, category_id=payload.category_id
            )
        if payload.supplier_id is not None:
            await GetSupplierUseCase(connection_manager=self._connections).execute(
                tenant_id=tenant_id, database_name=database_name, supplier_id=payload.supplier_id
            )

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            repository = ProductRepository(session)

            if await repository.get_by_sku(payload.sku) is not None:
                raise ConflictError(
                    "Já existe um produto com este SKU.", code="PRODUCT_SKU_ALREADY_EXISTS"
                )
            if payload.barcode and await repository.get_by_barcode(payload.barcode) is not None:
                raise ConflictError(
                    "Já existe um produto com este código de barras.",
                    code="PRODUCT_BARCODE_ALREADY_EXISTS",
                )

            product = Product(**payload.model_dump())
            await repository.create(product)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="PRODUCT_CREATED",
                resource="products",
                after=serialize_product(product),
            )
            await session.commit()

            return ProductResponse.model_validate(product)
