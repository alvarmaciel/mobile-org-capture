from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from captura_movil.capture import Capture
from captura_movil.ingest import Ingester
from captura_movil.spool import Spool


def test_offline_ingestion_retains_all_failed_captures(runtime_paths, block_sockets):
    spool = Spool(runtime_paths["queue"])
    captures = [Capture.create(f"Nota {number}", number, datetime.now(UTC)) for number in range(100)]
    for capture in captures:
        spool.publish(capture)
    ingester = Ingester(spool, runtime_paths["inbox"])
    async def sweep_without_network():
        block_sockets()
        return await ingester.sweep()

    assert len(asyncio.run(sweep_without_network())) == 100
    assert spool.pending_paths() == []
    assert len(list(spool.done.glob("*.txt"))) == 100
