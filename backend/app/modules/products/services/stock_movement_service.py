"""Serviço de domínio para aplicar uma movimentação de estoque. Recebe a sessão já
aberta pelo chamador — nunca abre a própria sessão nem comita — para permitir que outros
módulos (ex.: `service_orders`, ao concluir uma Ordem de Serviço) apliquem uma ou mais
movimentações na MESMA transação de uma operação maior, sem acessar
`ProductRepository`/`StockMovementRepository` diretamente (essas classes são o
`repository` do módulo `products/`; `services/` é a camada de comunicação entre módulos
que `app/modules/README.md` prevê para este caso)."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.exceptions import ConflictError, NotFoundError
from veloai_shared.schema.tenant import StockMovement

from app.modules.products.repositories.product_repository import ProductRepository
from app.modules.products.repositories.stock_movement_repository import (
    StockMovementRepository,
)
from app.modules.products.schemas.stock_movement import StockMovementType


def _compute_current_stock(previous_stock: int, movement: StockMovementType, quantity: int) -> int:
    if movement == "in":
        return previous_stock + quantity
    if movement == "out":
        return previous_stock - quantity
    return quantity  # "adjustment": quantity é o novo valor absoluto


async def apply_stock_movement(
    session: AsyncSession,
    *,
    product_id: uuid.UUID,
    movement: StockMovementType,
    quantity: int,
    reason: str,
) -> StockMovement:
    """Calcula o novo estoque, atualiza `Product.stock` e insere a linha de histórico —
    usando a sessão recebida, sem comitar. O chamador controla a transação (e deve
    comitar quando tudo mais que precisar acontecer na mesma operação também tiver dado
    certo)."""

    product_repository = ProductRepository(session)
    product = await product_repository.get_by_id(product_id)
    if product is None:
        raise NotFoundError("Produto não encontrado.", code="PRODUCT_NOT_FOUND")

    previous_stock = product.stock
    current_stock = _compute_current_stock(previous_stock, movement, quantity)
    if current_stock < 0:
        raise ConflictError(
            "Estoque insuficiente para esta movimentação.", code="STOCK_INSUFFICIENT"
        )

    await product_repository.update(product, {"stock": current_stock})

    movement_row = StockMovement(
        product_id=product_id,
        movement=movement,
        quantity=quantity,
        previous_stock=previous_stock,
        current_stock=current_stock,
        reason=reason,
    )
    await StockMovementRepository(session).create(movement_row)
    return movement_row
