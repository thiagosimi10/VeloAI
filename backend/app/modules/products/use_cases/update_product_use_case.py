"""Caso de uso: atualizar produto (atualização parcial)."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import ConflictError, NotFoundError

from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.categories.use_cases.get_category_use_case import GetCategoryUseCase
from app.modules.products.repositories.product_repository import ProductRepository
from app.modules.products.schemas.product import ProductResponse, UpdateProductRequest
from app.modules.products.use_cases._helpers import serialize_product
from app.modules.suppliers.use_cases.get_supplier_use_case import GetSupplierUseCase


class UpdateProductUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        product_id: uuid.UUID,
        payload: UpdateProductRequest,
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
            product = await repository.get_by_id(product_id)
            if product is None:
                raise NotFoundError("Produto não encontrado.", code="PRODUCT_NOT_FOUND")

            if (
                payload.barcode is not None
                and payload.barcode != product.barcode
                and await repository.get_by_barcode(payload.barcode) is not None
            ):
                raise ConflictError(
                    "Já existe um produto com este código de barras.",
                    code="PRODUCT_BARCODE_ALREADY_EXISTS",
                )

            before = serialize_product(product)
            update_data = payload.model_dump(exclude_unset=True)
            await repository.update(product, update_data)

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="PRODUCT_UPDATED",
                resource="products",
                before=before,
                after=serialize_product(product),
            )
            await session.commit()

            return ProductResponse.model_validate(product)
