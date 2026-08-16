from __future__ import annotations

from datetime import UTC, datetime

from captura_movil.capture import Capture
from captura_movil.spool import Spool


def test_pending_count_and_titles(runtime_paths):
    spool = Spool(runtime_paths["queue"])
    for title in ("uno", "dos", "tres"):
        spool.publish(Capture.create(title, 1, datetime.now(UTC)))
    assert spool.pending_titles() == ["dos", "tres", "uno"] or sorted(spool.pending_titles()) == ["dos", "tres", "uno"]
