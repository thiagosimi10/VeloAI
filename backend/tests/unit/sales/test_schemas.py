import uuid
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.sales.schemas.sale_item import AddSaleItemRequest, SaleItemResponse


def test_add_item_request_defaults_quantity_to_one() -> None:
    request = AddSaleItemRequest(product_id=uuid.uuid4())

    assert request.quantity == 1
    assert request.unit_price is None


def test_add_item_request_rejects_zero_quantity() -> None:
    with pytest.raises(ValidationError):
        AddSaleItemRequest(product_id=uuid.uuid4(), quantity=0)


def test_add_item_request_rejects_negative_unit_price() -> None:
    with pytest.raises(ValidationError):
        AddSaleItemRequest(product_id=uuid.uuid4(), unit_price=Decimal("-1.00"))


def test_sale_item_response_computes_total() -> None:
    response = SaleItemResponse(
        id=uuid.uuid4(),
        sale_id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        quantity=3,
        unit_price=Decimal("10.50"),
    )

    assert response.total == Decimal("31.50")
