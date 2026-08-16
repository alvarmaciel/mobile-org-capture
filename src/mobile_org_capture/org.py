"""Append-only Org heading rendering."""

from __future__ import annotations

from pathlib import Path

from .atomic import append_bytes
from .capture import Capture


def _escape_body_line(line: str) -> str:
    """Prevent a body line from being parsed as a new Org heading."""
    return " " + line if line.startswith("*") else line


def render_heading(capture: Capture) -> str:
    lines = [f"* TODO {capture.title}", ":PROPERTIES:", f":CAPTURED: {capture.received_at}", ":END:"]
    if capture.body:
        lines.extend(_escape_body_line(line) for line in capture.body.split("\n"))
    lines.extend(artifact.org_link for artifact in capture.artifacts)
    lines.extend(f"Adjunto descartado por tamaño: {item}" for item in capture.rejected_attachments)
    return "\n".join(lines) + "\n\n"


def append_capture(path: Path, capture: Capture) -> None:
    append_bytes(path, render_heading(capture).encode("utf-8"))
