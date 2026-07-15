import uuid

import pytest
from pydantic import ValidationError

from app.modules.service_orders.schemas.service_order_item import AddServiceOrderItemRequest


def test_add_item_request_accepts_product_only() -> None:
    request = AddServiceOrderItemRequest(product_id=uuid.uuid4(), quantity=2)

    assert request.service_id is None


def test_add_item_request_accepts_service_only() -> None:
    request = AddServiceOrderItemRequest(service_id=uuid.uuid4(), quantity=1)

    assert request.product_id is None


def test_add_item_request_rejects_both_product_and_service() -> None:
    with pytest.raises(ValidationError):
        AddServiceOrderItemRequest(product_id=uuid.uuid4(), service_id=uuid.uuid4())


def test_add_item_request_rejects_neither_product_nor_service() -> None:
    with pytest.raises(ValidationError):
        AddServiceOrderItemRequest(quantity=1)


def test_add_item_request_rejects_zero_quantity() -> None:
    with pytest.raises(ValidationError):
        AddServiceOrderItemRequest(product_id=uuid.uuid4(), quantity=0)
