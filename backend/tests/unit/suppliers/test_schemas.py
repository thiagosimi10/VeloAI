import pytest
from pydantic import ValidationError

from app.modules.suppliers.schemas.supplier import CreateSupplierRequest


def test_create_supplier_request_normalizes_document() -> None:
    request = CreateSupplierRequest(
        type="PJ", name="Tech Distribuidora LTDA", document="12.345.678/0001-99"
    )

    assert request.document == "12345678000199"


def test_create_supplier_request_defaults_country_to_brasil() -> None:
    request = CreateSupplierRequest(
        type="PJ", name="Tech Distribuidora LTDA", document="12345678000199"
    )

    assert request.country == "Brasil"


def test_create_supplier_request_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        CreateSupplierRequest(type="XX", name="Inválido", document="12345678901")  # type: ignore[arg-type]


def test_create_supplier_request_rejects_invalid_document() -> None:
    with pytest.raises(ValidationError):
        CreateSupplierRequest(type="PJ", name="Tech Distribuidora LTDA", document="123")


def test_create_supplier_request_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        CreateSupplierRequest(
            type="PJ",
            name="Tech Distribuidora LTDA",
            document="12345678000199",
            email="nao-e-email",
        )
