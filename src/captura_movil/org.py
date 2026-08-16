"""Append-only Org heading rendering."""

from __future__ import annotations

from .atomic import append_bytes
from .capture import Capture


def render_heading(capture: Capture) -> str:
    lines = [f"* TODO {capture.title}", ":PROPERTIES:", f":CAPTURED: {capture.received_at}", ":END:"]
    if capture.body:
        lines.extend([capture.body])
    lines.extend(artifact.org_link for artifact in capture.artifacts)
    lines.extend(f"Adjunto descartado por tamaño: {item}" for item in capture.rejected_attachments)
    return "\n".join(lines) + "\n"


def append_capture(path, capture: Capture) -> None:
    append_bytes(path, render_heading(capture).encode("utf-8"))
