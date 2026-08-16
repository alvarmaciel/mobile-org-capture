"""Local queue sweeps with deliberate at-least-once delivery."""

from __future__ import annotations

import asyncio
from pathlib import Path

from .org import append_capture
from .spool import Spool


class Ingester:
    def __init__(self, spool: Spool, inbox_path: Path) -> None:
        self.spool = spool
        self.inbox_path = inbox_path
        self._lock = asyncio.Lock()

    async def sweep(self) -> list[str]:
        async with self._lock:
            completed: list[str] = []
            for path in self.spool.pending_paths():
                capture = self.spool.load(path)
                try:
                    append_capture(self.inbox_path, capture)
                    self.spool.mark_done(path)
                except OSError:
                    continue
                completed.append(capture.capture_id)
            return completed
