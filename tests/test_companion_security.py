import pytest

from companion.server import CompanionConfig


TOKEN = "0123456789abcdef0123456789abcdef"


def test_loopback_can_run_without_tls() -> None:
    config = CompanionConfig(token=TOKEN)
    assert config.is_non_loopback is False
    assert config.tls_enabled is False


def test_non_loopback_requires_certificate_and_key() -> None:
    with pytest.raises(ValueError, match="TLS certificate and key are required"):
        CompanionConfig(host="0.0.0.0", token=TOKEN)


def test_certificate_and_key_must_be_provided_together() -> None:
    with pytest.raises(ValueError, match="certfile and keyfile"):
        CompanionConfig(token=TOKEN, certfile="server.pem")


def test_tls_is_enabled_when_both_files_are_configured() -> None:
    config = CompanionConfig(
        host="0.0.0.0",
        token=TOKEN,
        certfile="server.pem",
        keyfile="server-key.pem",
    )
    assert config.is_non_loopback is True
    assert config.tls_enabled is True
