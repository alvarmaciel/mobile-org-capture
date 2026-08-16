from __future__ import annotations

from datetime import UTC, datetime

from captura_movil.capture import Capture
from captura_movil.org import append_capture, render_heading


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
    assert content.endswith("\n\n") 

def test_body_line_starting_with_asterisk_is_escaped():
    capture = Capture.create("Camping\nLlevar:\n* carpa\n* bolsa", 2, datetime.now(UTC))
    rendered = render_heading(capture)
    heading_lines = [l for l in rendered.split("\n") if l.startswith("* ")]
    assert len(heading_lines) == 1
    assert " * carpa" in rendered
