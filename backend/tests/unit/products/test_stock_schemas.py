import pytest
from pydantic import ValidationError

from app.modules.products.schemas.stock_movement import CreateStockMovementRequest


def test_create_stock_movement_request_accepts_valid_in_movement() -> None:
    request = CreateStockMovementRequest(movement="in", quantity=5, reason="Compra de reposição")

    assert request.quantity == 5


def test_create_stock_movement_request_allows_zero_quantity_for_adjustment() -> None:
    request = CreateStockMovementRequest(
        movement="adjustment", quantity=0, reason="Contagem revelou estoque zerado"
    )

    assert request.quantity == 0


def test_create_stock_movement_request_rejects_zero_quantity_for_in() -> None:
    with pytest.raises(ValidationError):
        CreateStockMovementRequest(movement="in", quantity=0, reason="Compra de reposição")


def test_create_stock_movement_request_rejects_zero_quantity_for_out() -> None:
    with pytest.raises(ValidationError):
        CreateStockMovementRequest(movement="out", quantity=0, reason="Venda balcão")


def test_create_stock_movement_request_rejects_negative_quantity() -> None:
    with pytest.raises(ValidationError):
        CreateStockMovementRequest(movement="in", quantity=-1, reason="Compra de reposição")


def test_create_stock_movement_request_rejects_short_reason() -> None:
    with pytest.raises(ValidationError):
        CreateStockMovementRequest(movement="in", quantity=5, reason="ok")
