from __future__ import annotations

from datetime import UTC, datetime

from captura_movil.capture import Capture


def test_first_line_is_title_and_links_are_verbatim():
    capture = Capture.create("Título\nhttps://example.test/a", 1, datetime.now(UTC))
    assert capture.title == "Título"
    assert capture.body == "https://example.test/a"


def test_empty_first_line_uses_default_title():
    capture = Capture.create("\ncuerpo", 1, datetime.now(UTC))
    assert capture.title == "Sin título"
    assert capture.body == "cuerpo"
