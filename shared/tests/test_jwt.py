from datetime import timedelta

import pytest

from veloai_shared.security.jwt import (
    TokenExpiredError,
    TokenInvalidError,
    create_token,
    decode_token,
)


def test_create_and_decode_token_roundtrip() -> None:
    token = create_token(
        subject="user-123",
        secret="test-secret",
        expires_delta=timedelta(minutes=15),
        extra_claims={"tenant_id": "tenant-abc", "role": "Administrador"},
    )

    payload = decode_token(token, secret="test-secret")

    assert payload["sub"] == "user-123"
    assert payload["tenant_id"] == "tenant-abc"
    assert payload["role"] == "Administrador"
    assert "jti" in payload


def test_two_tokens_for_the_same_subject_have_different_jti() -> None:
    first = decode_token(
        create_token(subject="user-1", secret="s", expires_delta=timedelta(minutes=5)),
        secret="s",
    )
    second = decode_token(
        create_token(subject="user-1", secret="s", expires_delta=timedelta(minutes=5)),
        secret="s",
    )

    assert first["jti"] != second["jti"]


def test_decode_expired_token_raises_token_expired_error() -> None:
    token = create_token(
        subject="user-123", secret="test-secret", expires_delta=timedelta(seconds=-1)
    )

    with pytest.raises(TokenExpiredError):
        decode_token(token, secret="test-secret")


def test_decode_with_wrong_secret_raises_token_invalid_error() -> None:
    token = create_token(subject="user-123", secret="correct-secret", expires_delta=timedelta(minutes=5))

    with pytest.raises(TokenInvalidError):
        decode_token(token, secret="wrong-secret")


def test_decode_malformed_token_raises_token_invalid_error() -> None:
    with pytest.raises(TokenInvalidError):
        decode_token("not-a-real-jwt", secret="test-secret")
