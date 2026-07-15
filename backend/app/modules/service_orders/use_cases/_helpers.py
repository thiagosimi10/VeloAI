"""Utilitários internos compartilhados entre os use cases de Ordens de Serviço."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.exceptions import ValidationError
from veloai_shared.schema.tenant import ServiceOrder

from app.modules.service_orders.repositories.service_order_item_repository import (
    ServiceOrderItemRepository,
)
from app.modules.service_orders.schemas.service_order import ServiceOrderResponse
from app.modules.service_orders.schemas.service_order_item import ServiceOrderItemResponse

# Transições permitidas nesta fase (fluxo simplificado — ver plano da Fase 8).
_ALLOWED_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "open": ("in_progress", "cancelled"),
    "in_progress": ("completed", "cancelled"),
    "completed": (),
    "cancelled": (),
}


def ensure_transition_allowed(order: ServiceOrder, target_status: str) -> None:
    allowed = _ALLOWED_TRANSITIONS.get(order.status, ())
    if target_status not in allowed:
        raise ValidationError(
            f"Não é possível mudar de '{order.status}' para '{target_status}'.",
            code="SERVICE_ORDER_INVALID_TRANSITION",
        )


def ensure_items_are_editable(order: ServiceOrder) -> None:
    if order.status in ("completed", "cancelled"):
        raise ValidationError(
            "Não é possível alterar itens de uma Ordem de Serviço "
            f"'{order.status}'.",
            code="SERVICE_ORDER_ITEMS_LOCKED",
        )


async def recalculate_order_total(
    session: AsyncSession, order: ServiceOrder, item_repository: ServiceOrderItemRepository
) -> Decimal:
    items = await item_repository.list_all_by_order(order.id)
    total = sum((item.total for item in items), Decimal("0.00"))
    order.total = total
    await session.flush()
    return total


def to_response(order: ServiceOrder) -> ServiceOrderResponse:
    """Converte `ServiceOrder` para `ServiceOrderResponse`. O modelo SQLAlchemy não tem
    uma relationship real para `items` (os itens são buscados à parte, via
    `ServiceOrderItemRepository`) — garante que o atributo exista antes de validar, em
    vez de depender do fallback para o default do campo Pydantic quando o atributo
    está ausente."""

    if not hasattr(order, "items"):
        order.items = []  # type: ignore[attr-defined]
    return ServiceOrderResponse.model_validate(order)


def serialize_order(order: ServiceOrder) -> dict[str, Any]:
    return to_response(order).model_dump(mode="json")


async def build_order_response(
    order: ServiceOrder, item_repository: ServiceOrderItemRepository
) -> ServiceOrderResponse:
    """Monta a resposta completa de uma OS, com os itens embutidos — usada na busca por
    id (não na listagem, que não carrega itens de cada linha)."""

    items = await item_repository.list_all_by_order(order.id)
    order.items = [  # type: ignore[attr-defined]
        ServiceOrderItemResponse.model_validate(item) for item in items
    ]
    return to_response(order)


def build_item_total(quantity: int, unit_price: Decimal) -> Decimal:
    return (Decimal(quantity) * unit_price).quantize(Decimal("0.01"))
