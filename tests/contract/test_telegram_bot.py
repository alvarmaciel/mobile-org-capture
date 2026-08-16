from __future__ import annotations

from types import SimpleNamespace

from captura_movil.bot import CaptureBot
from captura_movil.ingest import Ingester
from captura_movil.settings import Settings
from captura_movil.spool import Spool


def test_authorization_checks_chat_before_processing(runtime_paths):
    settings = Settings.from_environment({
        "TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_ALLOWED_CHAT_ID": "12", "CAPTURE_QUEUE_DIR": str(runtime_paths["queue"]),
        "ORG_INBOX_PATH": str(runtime_paths["inbox"]), "ORG_ARTIFACTS_DIR": str(runtime_paths["artifacts"]),
        "ORG_ARTIFACTS_LINK_PREFIX": "artifact:", "CAPTURE_TIMEZONE": "UTC", "MAX_ATTACHMENT_BYTES": "10", "CAPTURE_SWEEP_INTERVAL": "1",
    })
    bot = CaptureBot(settings, Spool(settings.queue_dir), Ingester(Spool(settings.queue_dir), settings.inbox_path))
    assert bot.authorized(SimpleNamespace(effective_message=SimpleNamespace(chat_id=12)))
    assert not bot.authorized(SimpleNamespace(effective_message=SimpleNamespace(chat_id=13)))
