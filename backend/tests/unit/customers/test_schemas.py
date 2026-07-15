import pytest
from pydantic import ValidationError

from app.modules.customers.schemas.customer import CreateCustomerRequest


def test_create_customer_request_normalizes_document() -> None:
    request = CreateCustomerRequest(
        type="PF", name="João Silva", document="123.456.789-01"
    )

    assert request.document == "12345678901"


def test_create_customer_request_defaults_country_to_brasil() -> None:
    request = CreateCustomerRequest(type="PJ", name="Empresa LTDA", document="12345678000199")

    assert request.country == "Brasil"


def test_create_customer_request_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        CreateCustomerRequest(type="XX", name="Inválido", document="12345678901")  # type: ignore[arg-type]


def test_create_customer_request_rejects_invalid_document() -> None:
    with pytest.raises(ValidationError):
        CreateCustomerRequest(type="PF", name="João Silva", document="123")


def test_create_customer_request_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        CreateCustomerRequest(
            type="PF", name="João Silva", document="12345678901", email="nao-e-email"
        )
