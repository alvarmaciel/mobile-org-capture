from __future__ import annotations

from datetime import UTC, datetime

from captura_movil.capture import Capture
from captura_movil.org import append_capture


def test_append_never_rewrites_existing_inbox(runtime_paths):
    inbox = runtime_paths["inbox"]
    inbox.parent.mkdir(parents=True, exist_ok=True)
    inbox.write_text("* Existing\n", encoding="utf-8")
    capture = Capture.create("Nueva\ncuerpo", 1, datetime.now(UTC))
    append_capture(inbox, capture)
    content = inbox.read_text(encoding="utf-8")
    assert content.startswith("* Existing\n")
    assert "* TODO Nueva" in content
    assert capture.received_at in content
