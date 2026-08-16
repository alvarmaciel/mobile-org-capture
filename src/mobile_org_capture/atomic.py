"""Durable local file operations used by every publication path."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def fsync_directory(directory: Path) -> None:
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def publish_bytes(path: Path, data: bytes) -> None:
    """Publish data only after it is completely durable in the final directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
        fsync_directory(path.parent)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def append_bytes(path: Path, data: bytes) -> None:
    """Durably append bytes without reading, rewriting, or truncating the file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)


def move_durable(source: Path, destination: Path) -> None:
    """Move on the same filesystem and make the directory entry durable."""
    if source.parent != destination.parent and source.stat().st_dev != destination.parent.stat().st_dev:
        raise ValueError("source and destination must be on the same filesystem")
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.replace(source, destination)
    fsync_directory(destination.parent)
