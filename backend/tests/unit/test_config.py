import os

from app.core.config import Settings, get_settings


def test_settings_default_values() -> None:
    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.app_name == "VeloAI Backend"
    assert settings.api_v1_prefix == "/api/v1"


def test_settings_reads_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("APP_NAME", "VeloAI Backend Test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.app_name == "VeloAI Backend Test"
    assert settings.log_level == "DEBUG"


def test_cors_origins_list_splits_and_trims() -> None:
    settings = Settings(_env_file=None, cors_allowed_origins="http://a.com, http://b.com")  # type: ignore[call-arg]

    assert settings.cors_origins_list == ["http://a.com", "http://b.com"]


def test_get_settings_is_cached() -> None:
    os.environ.setdefault("APP_NAME", "VeloAI Backend")

    assert get_settings() is get_settings()
