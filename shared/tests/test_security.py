import uuid

from veloai_shared.security import hash_password, needs_rehash, new_uuid7, verify_password
from veloai_shared.security.ids import short_id


def test_hash_password_is_never_plain_text() -> None:
    hashed = hash_password("Sup3rSecret!")

    assert hashed != "Sup3rSecret!"
    assert hashed.startswith("$argon2id$")


def test_verify_password_success_and_failure() -> None:
    hashed = hash_password("Sup3rSecret!")

    assert verify_password("Sup3rSecret!", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_needs_rehash_false_for_fresh_hash() -> None:
    hashed = hash_password("Sup3rSecret!")

    assert needs_rehash(hashed) is False


def test_new_uuid7_generates_valid_sortable_uuid() -> None:
    first = new_uuid7()
    second = new_uuid7()

    assert isinstance(first, uuid.UUID)
    assert first.version == 7
    assert first != second
    # UUIDv7 é ordenável por tempo de criação.
    assert str(first) < str(second)


def test_short_id_returns_12_hex_chars() -> None:
    value = new_uuid7()

    result = short_id(value)

    assert len(result) == 12
    assert all(c in "0123456789abcdef" for c in result)
