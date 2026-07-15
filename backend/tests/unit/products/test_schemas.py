from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.products.schemas.product import CreateProductRequest, ProductResponse
import uuid
from datetime import UTC, datetime


def test_create_product_request_accepts_valid_payload() -> None:
    request = CreateProductRequest(
        sku="SSD-KGN-1TB",
        name="SSD Kingston 1TB",
        cost_price=Decimal("320.00"),
        sale_price=Decimal("490.00"),
    )

    assert request.unit == "UN"
    assert request.stock == 0


def test_create_product_request_rejects_negative_cost_price() -> None:
    with pytest.raises(ValidationError):
        CreateProductRequest(
            sku="SSD-KGN-1TB",
            name="SSD Kingston 1TB",
            cost_price=Decimal("-1.00"),
            sale_price=Decimal("490.00"),
        )


def test_create_product_request_rejects_negative_stock() -> None:
    with pytest.raises(ValidationError):
        CreateProductRequest(
            sku="SSD-KGN-1TB",
            name="SSD Kingston 1TB",
            cost_price=Decimal("320.00"),
            sale_price=Decimal("490.00"),
            stock=-5,
        )


def test_product_response_computes_margin_and_percentage() -> None:
    response = ProductResponse(
        id=uuid.uuid4(),
        category_id=None,
        supplier_id=None,
        sku="SSD-KGN-1TB",
        barcode=None,
        name="SSD Kingston 1TB",
        description=None,
        cost_price=Decimal("320.00"),
        sale_price=Decimal("490.00"),
        stock=20,
        minimum_stock=None,
        maximum_stock=None,
        unit="UN",
        weight=None,
        active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    assert response.margin == Decimal("170.00")
    # 170/320 * 100 = 53.125 exatamente; Decimal.__round__ usa ROUND_HALF_EVEN por
    # padrão, então o resultado arredonda para o par mais próximo: 53.12 (não 53.13).
    assert response.margin_percentage == Decimal("53.12")


def test_product_response_margin_percentage_is_none_when_cost_is_zero() -> None:
    response = ProductResponse(
        id=uuid.uuid4(),
        category_id=None,
        supplier_id=None,
        sku="BRINDE-001",
        barcode=None,
        name="Brinde",
        description=None,
        cost_price=Decimal("0.00"),
        sale_price=Decimal("10.00"),
        stock=5,
        minimum_stock=None,
        maximum_stock=None,
        unit="UN",
        weight=None,
        active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    assert response.margin_percentage is None
