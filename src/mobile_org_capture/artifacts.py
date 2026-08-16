"""Durable artifact naming and publication."""

from __future__ import annotations

import mimetypes
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from .atomic import publish_bytes
from .capture import Artifact


def normalized_filename(name: str | None, capture_id: str, received_at: datetime, content_type: str | None) -> str:
    extension = Path(name or "").suffix
    if not extension:
        extension = mimetypes.guess_extension(content_type or "") or ".bin"
    stem = Path(name or "artifact").stem
    stem = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode()
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip(".-") or "artifact"
    timestamp = received_at.strftime("%Y%m%dT%H%M%S%z")
    return f"{timestamp}-{capture_id[:12]}-{stem}{extension.lower()}"


def publish_artifact(
    directory: Path,
    prefix: str,
    data: bytes,
    name: str | None,
    capture_id: str,
    received_at: datetime,
    content_type: str | None,
) -> Artifact:
    filename = normalized_filename(name, capture_id, received_at, content_type)
    path = directory / filename
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing artifact: {path}")
    publish_bytes(path, data)
    return Artifact(filename=filename, size_bytes=len(data), org_link=f"[[{prefix}{filename}][{filename}]]")
