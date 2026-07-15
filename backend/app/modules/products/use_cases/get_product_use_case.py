"""Caso de uso: buscar um produto pelo id."""

from __future__ import annotations

import uuid

from veloai_shared.exceptions import NotFoundError

from app.core.database import TenantConnectionManager
from app.modules.products.repositories.product_repository import ProductRepository
from app.modules.products.schemas.product import ProductResponse


class GetProductUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self, *, tenant_id: uuid.UUID, database_name: str, product_id: uuid.UUID
    ) -> ProductResponse:
        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            product = await ProductRepository(session).get_by_id(product_id)
            if product is None:
                raise NotFoundError("Produto não encontrado.", code="PRODUCT_NOT_FOUND")
            return ProductResponse.model_validate(product)
