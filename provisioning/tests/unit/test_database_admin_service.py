import pytest

from app.services.database_admin_service import DatabaseAdminService


@pytest.mark.parametrize(
    "database_name",
    ["tenant_2ab34f9c1a0b", "tenant_abc", "veloai_master_test"],
)
def test_assert_valid_name_accepts_expected_patterns(database_name: str) -> None:
    # Não deve levantar exceção.
    DatabaseAdminService._assert_valid_name(database_name)


@pytest.mark.parametrize(
    "database_name",
    [
        "tenant_2ab34f9c1a0b; DROP TABLE users;",
        "Tenant_Uppercase",
        "",
        "1_starts_with_number",
        "tenant name with spaces",
    ],
)
def test_assert_valid_name_rejects_unsafe_or_invalid_names(database_name: str) -> None:
    with pytest.raises(ValueError):
        DatabaseAdminService._assert_valid_name(database_name)
