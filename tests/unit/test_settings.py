from __future__ import annotations

import pytest

from mobile_org_capture.settings import Settings


def test_settings_accepts_complete_environment(runtime_paths):
    settings = Settings.from_environment({
        "TELEGRAM_BOT_TOKEN": "token",
        "TELEGRAM_ALLOWED_CHAT_ID": "12",
        "CAPTURE_QUEUE_DIR": str(runtime_paths["queue"]),
        "ORG_INBOX_PATH": str(runtime_paths["inbox"]),
        "ORG_ARTIFACTS_DIR": str(runtime_paths["artifacts"]),
        "ORG_ARTIFACTS_LINK_PREFIX": "artifact:",
        "CAPTURE_TIMEZONE": "America/Argentina/Buenos_Aires",
        "MAX_ATTACHMENT_BYTES": "10",
        "CAPTURE_SWEEP_INTERVAL": "1",
    })
    assert settings.telegram_allowed_chat_id == 12


def test_settings_rejects_invalid_timezone(runtime_paths):
    env = {
        "TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_ALLOWED_CHAT_ID": "12",
        "CAPTURE_QUEUE_DIR": str(runtime_paths["queue"]), "ORG_INBOX_PATH": str(runtime_paths["inbox"]),
        "ORG_ARTIFACTS_DIR": str(runtime_paths["artifacts"]), "ORG_ARTIFACTS_LINK_PREFIX": "artifact:",
        "CAPTURE_TIMEZONE": "not-a-zone", "MAX_ATTACHMENT_BYTES": "10", "CAPTURE_SWEEP_INTERVAL": "1",
    }
    with pytest.raises(ValueError, match="IANA"):
        Settings.from_environment(env)
