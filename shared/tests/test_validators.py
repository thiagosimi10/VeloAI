import pytest

from veloai_shared.validators import normalize_document


def test_normalize_document_strips_cnpj_mask() -> None:
    assert normalize_document("12.345.678/0001-99") == "12345678000199"


def test_normalize_document_strips_cpf_mask() -> None:
    assert normalize_document("123.456.789-01") == "12345678901"


def test_normalize_document_accepts_already_unmasked_values() -> None:
    assert normalize_document("12345678901") == "12345678901"


@pytest.mark.parametrize("value", ["123", "1234567890123456", "", "abc.def.ghi-jk"])
def test_normalize_document_rejects_invalid_length(value: str) -> None:
    with pytest.raises(ValueError, match="CPF"):
        normalize_document(value)
