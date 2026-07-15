"""Utilitários internos compartilhados entre os use cases de Vendas — mesmo formato de
`service_orders/use_cases/_helpers.py`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.exceptions import ValidationError
from veloai_shared.schema.tenant import Sale

from app.modules.sales.repositories.sale_item_repository import SaleItemRepository
from app.modules.sales.schemas.sale import SaleResponse
from app.modules.sales.schemas.sale_item import SaleItemResponse

# Transições permitidas nesta fase (fluxo simplificado — ver plano da Fase 9). Depois de
# `paid`, o estoque já foi consumido e não há estorno nesta fase, por isso não há saída.
_ALLOWED_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "open": ("paid", "cancelled"),
    "paid": (),
    "cancelled": (),
}


def ensure_transition_allowed(sale: Sale, target_status: str) -> None:
    allowed = _ALLOWED_TRANSITIONS.get(sale.status, ())
    if target_status not in allowed:
        raise ValidationError(
            f"Não é possível mudar de '{sale.status}' para '{target_status}'.",
            code="SALE_INVALID_TRANSITION",
        )


def ensure_sale_is_editable(sale: Sale) -> None:
    """Usada tanto para itens quanto para os campos gerais (`discount`/
    `payment_method`) — depois de `paid`/`cancelled` a venda está financeiramente
    encerrada, nada mais deve mudar (mesmo espírito de `ensure_items_are_editable` de
    Ordens de Serviço, só que aqui a trava vale para a venda inteira, não só os itens)."""

    if sale.status != "open":
        raise ValidationError(
            f"Não é possível alterar uma Venda '{sale.status}'.",
            code="SALE_NOT_EDITABLE",
        )


async def recalculate_sale_total(
    session: AsyncSession, sale: Sale, item_repository: SaleItemRepository
) -> Decimal:
    """`sale_items` não tem coluna `total` — o total de cada item é sempre calculado
    (`quantity * unit_price`), nunca persistido. O total da venda é a soma desses
    valores menos o desconto, nunca negativo."""

    items = await item_repository.list_all_by_sale(sale.id)
    subtotal = sum((item.quantity * item.unit_price for item in items), Decimal("0.00"))
    total = max(subtotal - sale.discount, Decimal("0.00")).quantize(Decimal("0.01"))
    sale.total = total
    await session.flush()
    return total


def to_response(sale: Sale) -> SaleResponse:
    """Converte `Sale` para `SaleResponse`. O modelo SQLAlchemy não tem uma
    relationship real para `items` (os itens são buscados à parte, via
    `SaleItemRepository`) — garante que o atributo exista antes de validar, em vez de
    depender do fallback para o default do campo Pydantic quando o atributo está
    ausente."""

    if not hasattr(sale, "items"):
        sale.items = []  # type: ignore[attr-defined]
    return SaleResponse.model_validate(sale)


def serialize_sale(sale: Sale) -> dict[str, Any]:
    return to_response(sale).model_dump(mode="json")


async def build_sale_response(sale: Sale, item_repository: SaleItemRepository) -> SaleResponse:
    """Monta a resposta completa de uma venda, com os itens embutidos — usada na busca
    por id (não na listagem, que não carrega itens de cada linha)."""

    items = await item_repository.list_all_by_sale(sale.id)
    sale.items = [  # type: ignore[attr-defined]
        SaleItemResponse.model_validate(item) for item in items
    ]
    return to_response(sale)
