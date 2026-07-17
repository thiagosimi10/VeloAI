import uuid
from datetime import timedelta

import pytest
from veloai_shared.security.jwt import TokenInvalidError, create_token

from app.core.config import Settings
from app.modules.admin.services.platform_admin_token_service import PlatformAdminTokenService


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,  # type: ignore[call-arg]
        platform_admin_jwt_secret="admin-secret",
        platform_admin_token_expire_minutes=60,
        jwt_secret="tenant-secret",
    )


@pytest.fixture
def token_service(settings: Settings) -> PlatformAdminTokenService:
    return PlatformAdminTokenService(settings)


def test_token_roundtrip(token_service: PlatformAdminTokenService) -> None:
    admin_id = uuid.uuid4()

    token = token_service.issue_token(admin_id=admin_id)
    claims = token_service.decode_token(token)

    assert claims.admin_id == admin_id


def test_token_uses_its_own_secret_independent_from_tenant_jwt_secret(
    settings: Settings,
) -> None:
    service = PlatformAdminTokenService(settings)
    token = service.issue_token(admin_id=uuid.uuid4())

    wrong_settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        platform_admin_jwt_secret="different-admin-secret",
        jwt_secret="tenant-secret",
    )
    wrong_service = PlatformAdminTokenService(wrong_settings)

    with pytest.raises(Exception):  # noqa: B017,PT011 - TokenInvalidError/TokenExpiredError
        wrong_service.decode_token(token)


def test_decode_rejects_a_token_without_the_platform_admin_type_claim(
    settings: Settings,
) -> None:
    foreign_token = create_token(
        subject=str(uuid.uuid4()),
        secret=settings.platform_admin_jwt_secret,
        expires_delta=timedelta(minutes=5),
        extra_claims={"type": "access"},
    )
    service = PlatformAdminTokenService(settings)

    with pytest.raises(TokenInvalidError):
        service.decode_token(foreign_token)
