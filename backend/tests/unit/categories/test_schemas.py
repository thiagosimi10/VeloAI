import pytest
from pydantic import ValidationError

from app.modules.categories.schemas.category import CreateCategoryRequest


def test_create_category_request_accepts_valid_payload() -> None:
    request = CreateCategoryRequest(name="Armazenamento", description="SSDs e HDs")

    assert request.name == "Armazenamento"
    assert request.description == "SSDs e HDs"


def test_create_category_request_allows_missing_description() -> None:
    request = CreateCategoryRequest(name="Armazenamento")

    assert request.description is None


def test_create_category_request_rejects_too_short_name() -> None:
    with pytest.raises(ValidationError):
        CreateCategoryRequest(name="A")
