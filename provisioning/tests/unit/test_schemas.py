import pytest
from pydantic import ValidationError

from app.schemas.tenant import CreateTenantRequest


def test_create_tenant_request_normalizes_document() -> None:
    request = CreateTenantRequest(
        legal_name="Empresa Teste LTDA",
        document="12.345.678/0001-99",
        admin_name="João Silva",
        admin_email="joao@empresa.test",
    )

    assert request.document == "12345678000199"


def test_create_tenant_request_rejects_invalid_document_length() -> None:
    with pytest.raises(ValidationError):
        CreateTenantRequest(
            legal_name="Empresa Teste LTDA",
            document="123",
            admin_name="João Silva",
            admin_email="joao@empresa.test",
        )


def test_create_tenant_request_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        CreateTenantRequest(
            legal_name="Empresa Teste LTDA",
            document="12345678901",
            admin_name="João Silva",
            admin_email="nao-e-um-email",
        )


def test_create_tenant_request_accepts_cpf() -> None:
    request = CreateTenantRequest(
        legal_name="Prestador Autônomo",
        document="123.456.789-01",
        admin_name="Ana Souza",
        admin_email="ana@prestador.test",
    )

    assert request.document == "12345678901"


def test_create_tenant_request_password_defaults_to_none() -> None:
    request = CreateTenantRequest(
        legal_name="Empresa Teste LTDA",
        document="12345678901",
        admin_name="João Silva",
        admin_email="joao@empresa.test",
    )

    assert request.password is None


def test_create_tenant_request_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        CreateTenantRequest(
            legal_name="Empresa Teste LTDA",
            document="12345678901",
            admin_name="João Silva",
            admin_email="joao@empresa.test",
            password="1234567",
        )
