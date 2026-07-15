from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.services.schemas.service import CreateServiceRequest


def test_create_service_request_accepts_valid_payload() -> None:
    request = CreateServiceRequest(
        name="Formatação de Computador", price=Decimal("180.00"), estimated_time=60
    )

    assert request.name == "Formatação de Computador"
    assert request.estimated_time == 60


def test_create_service_request_allows_missing_estimated_time() -> None:
    request = CreateServiceRequest(name="Diagnóstico", price=Decimal("50.00"))

    assert request.estimated_time is None


def test_create_service_request_rejects_negative_price() -> None:
    with pytest.raises(ValidationError):
        CreateServiceRequest(name="Diagnóstico", price=Decimal("-1.00"))


def test_create_service_request_rejects_negative_estimated_time() -> None:
    with pytest.raises(ValidationError):
        CreateServiceRequest(name="Diagnóstico", price=Decimal("50.00"), estimated_time=-10)


def test_create_service_request_rejects_too_short_name() -> None:
    with pytest.raises(ValidationError):
        CreateServiceRequest(name="A", price=Decimal("50.00"))
