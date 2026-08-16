from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from captura_movil.capture import Capture
from captura_movil.ingest import Ingester
from captura_movil.spool import Spool


def test_one_hundred_text_captures_preserve_title_and_body(runtime_paths):
    spool = Spool(runtime_paths["queue"])
    for number in range(100):
        spool.publish(Capture.create(f"Título {number}\ncuerpo {number}", number, datetime.now(UTC)))
    completed = asyncio.run(Ingester(spool, runtime_paths["inbox"]).sweep())
    inbox = runtime_paths["inbox"].read_text(encoding="utf-8")
    assert len(completed) == 100
    assert "* TODO Título 99\n:PROPERTIES:" in inbox
    assert "cuerpo 99" in inbox
