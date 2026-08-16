"""Environment-only runtime configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    telegram_allowed_chat_id: int
    queue_dir: Path
    inbox_path: Path
    artifacts_dir: Path
    artifacts_link_prefix: str
    timezone: ZoneInfo
    max_attachment_bytes: int
    sweep_interval: int

    @classmethod
    def from_environment(cls, environment: dict[str, str] | None = None) -> "Settings":
        env = os.environ if environment is None else environment

        def required(name: str) -> str:
            value = env.get(name, "").strip()
            if not value:
                raise ValueError(f"missing required environment variable: {name}")
            return value

        def positive(name: str) -> int:
            try:
                value = int(required(name))
            except ValueError as error:
                raise ValueError(f"{name} must be an integer") from error
            if value <= 0:
                raise ValueError(f"{name} must be positive")
            return value

        def local_directory(name: str) -> Path:
            path = Path(required(name)).expanduser()
            if not path.is_absolute() or not path.is_dir():
                raise ValueError(f"{name} must be an existing absolute directory")
            return path

        queue_dir = local_directory("CAPTURE_QUEUE_DIR")
        artifacts_dir = local_directory("ORG_ARTIFACTS_DIR")
        inbox_path = Path(required("ORG_INBOX_PATH")).expanduser()
        if not inbox_path.is_absolute() or not inbox_path.parent.is_dir():
            raise ValueError("ORG_INBOX_PATH must have an existing absolute parent directory")
        prefix = required("ORG_ARTIFACTS_LINK_PREFIX")
        if not prefix.endswith(":"):
            raise ValueError("ORG_ARTIFACTS_LINK_PREFIX must end in ':'")
        try:
            timezone = ZoneInfo(required("CAPTURE_TIMEZONE"))
        except ZoneInfoNotFoundError as error:
            raise ValueError("CAPTURE_TIMEZONE must be an IANA time-zone name") from error
        try:
            chat_id = int(required("TELEGRAM_ALLOWED_CHAT_ID"))
        except ValueError as error:
            raise ValueError("TELEGRAM_ALLOWED_CHAT_ID must be an integer") from error
        return cls(
            telegram_bot_token=required("TELEGRAM_BOT_TOKEN"),
            telegram_allowed_chat_id=chat_id,
            queue_dir=queue_dir,
            inbox_path=inbox_path,
            artifacts_dir=artifacts_dir,
            artifacts_link_prefix=prefix,
            timezone=timezone,
            max_attachment_bytes=positive("MAX_ATTACHMENT_BYTES"),
            sweep_interval=positive("CAPTURE_SWEEP_INTERVAL"),
        )
