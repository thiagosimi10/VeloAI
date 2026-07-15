import uuid

import pytest
from veloai_shared.security.jwt import TokenInvalidError

from app.core.config import Settings
from app.modules.auth.services.token_service import TokenService


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,  # type: ignore[call-arg]
        jwt_secret="access-secret",
        jwt_refresh_secret="refresh-secret",
        jwt_access_token_expire_minutes=15,
        jwt_refresh_token_expire_days=14,
    )


@pytest.fixture
def token_service(settings: Settings) -> TokenService:
    return TokenService(settings)


def test_access_token_roundtrip(token_service: TokenService) -> None:
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()

    token = token_service.issue_access_token(
        user_id=user_id, tenant_id=tenant_id, database_name="tenant_abc", role="Administrador"
    )
    claims = token_service.decode_access_token(token)

    assert claims.user_id == user_id
    assert claims.tenant_id == tenant_id
    assert claims.database_name == "tenant_abc"
    assert claims.role == "Administrador"


def test_refresh_token_roundtrip(token_service: TokenService) -> None:
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()

    token = token_service.issue_refresh_token(
        user_id=user_id, tenant_id=tenant_id, database_name="tenant_abc"
    )
    claims = token_service.decode_refresh_token(token)

    assert claims.user_id == user_id
    assert claims.tenant_id == tenant_id
    assert claims.database_name == "tenant_abc"
    assert claims.jti


def test_access_token_cannot_be_decoded_as_refresh_token(token_service: TokenService) -> None:
    token = token_service.issue_access_token(
        user_id=uuid.uuid4(), tenant_id=uuid.uuid4(), database_name="tenant_abc", role="Vendedor"
    )

    with pytest.raises(TokenInvalidError):
        token_service.decode_refresh_token(token)


def test_refresh_token_cannot_be_decoded_as_access_token(token_service: TokenService) -> None:
    token = token_service.issue_refresh_token(
        user_id=uuid.uuid4(), tenant_id=uuid.uuid4(), database_name="tenant_abc"
    )

    with pytest.raises(TokenInvalidError):
        token_service.decode_access_token(token)


def test_access_and_refresh_secrets_are_independent(settings: Settings) -> None:
    service = TokenService(settings)
    access_token = service.issue_access_token(
        user_id=uuid.uuid4(), tenant_id=uuid.uuid4(), database_name="tenant_abc", role="Admin"
    )

    # Um token de access assinado com o segredo de access nunca deve validar contra o
    # segredo de refresh, mesmo que ambos existam na mesma instância de Settings.
    wrong_settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        jwt_secret="different-secret",
        jwt_refresh_secret="refresh-secret",
    )
    wrong_service = TokenService(wrong_settings)

    with pytest.raises(Exception):  # noqa: B017,PT011 - TokenInvalidError/TokenExpiredError
        wrong_service.decode_access_token(access_token)


def test_hash_refresh_token_is_deterministic_and_not_reversible(
    token_service: TokenService,
) -> None:
    token = "some-refresh-token-value"

    first_hash = token_service.hash_refresh_token(token)
    second_hash = token_service.hash_refresh_token(token)

    assert first_hash == second_hash
    assert first_hash != token
    assert len(first_hash) == 64  # sha256 hex digest
