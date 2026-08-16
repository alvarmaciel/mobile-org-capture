from __future__ import annotations

from datetime import UTC, datetime

from mobile_org_capture.capture import Capture
from mobile_org_capture.spool import Spool


def test_pending_count_and_titles(runtime_paths):
    spool = Spool(runtime_paths["queue"])
    for title in ("uno", "dos", "tres"):
        spool.publish(Capture.create(title, 1, datetime.now(UTC)))
    assert spool.pending_titles() == ["dos", "tres", "uno"] or sorted(spool.pending_titles()) == ["dos", "tres", "uno"]
