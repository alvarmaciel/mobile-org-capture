"""Filesystem-only immutable capture queue."""

from __future__ import annotations

import json
from pathlib import Path

from .atomic import move_durable, publish_bytes
from .capture import Capture


class Spool:
    def __init__(self, root: Path) -> None:
        self.pending = root / "pending"
        self.done = root / "done"
        self.pending.mkdir(parents=True, exist_ok=True)
        self.done.mkdir(parents=True, exist_ok=True)

    def path_for(self, capture: Capture) -> Path:
        safe_time = capture.received_at.replace(":", "").replace("+", "_")
        return self.pending / f"{safe_time}-{capture.capture_id}.txt"

    def publish(self, capture: Capture) -> Path:
        path = self.path_for(capture)
        publish_bytes(path, (json.dumps(capture.to_dict(), ensure_ascii=False, sort_keys=True) + "\n").encode())
        return path

    def load(self, path: Path) -> Capture:
        return Capture.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def pending_paths(self) -> list[Path]:
        return sorted(self.pending.glob("*.txt"))

    def pending_titles(self) -> list[str]:
        return [self.load(path).title for path in self.pending_paths()]

    def mark_done(self, path: Path) -> Path:
        destination = self.done / path.name
        move_durable(path, destination)
        return destination
