from __future__ import annotations

from datetime import UTC, datetime

from captura_movil.capture import Capture
from captura_movil.spool import Spool


def test_manifest_is_atomic_and_pending_titles_are_derived(runtime_paths):
    spool = Spool(runtime_paths["queue"])
    capture = Capture.create("Título\ncuerpo", 1, datetime.now(UTC))
    path = spool.publish(capture)
    assert path.exists()
    assert list(path.parent.glob("*.tmp")) == []
    assert spool.pending_titles() == ["Título"]
    spool.mark_done(path)
    assert spool.pending_titles() == []
