from __future__ import annotations

import socket
from pathlib import Path

import pytest


@pytest.fixture
def runtime_paths(tmp_path: Path) -> dict[str, Path]:
    queue = tmp_path / "queue"
    artifacts = tmp_path / "org" / "artifacts"
    queue.mkdir(parents=True)
    artifacts.mkdir(parents=True)
    return {"queue": queue, "artifacts": artifacts, "inbox": tmp_path / "org" / "inbox.org"}


@pytest.fixture
def block_sockets(monkeypatch):
    def activate():
        def blocked(*args, **kwargs):
            raise AssertionError("post-retention ingestion must not access the network")

        monkeypatch.setattr(socket, "create_connection", blocked)
        monkeypatch.setattr(socket, "getaddrinfo", blocked)

    return activate
