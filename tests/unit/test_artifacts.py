from __future__ import annotations

from datetime import UTC, datetime

import pytest

from mobile_org_capture.artifacts import publish_artifact


def test_artifact_uses_unique_normalized_name_and_abbreviation(runtime_paths):
    artifact = publish_artifact(runtime_paths["artifacts"], "artifact:", b"pdf", "fóto final.PDF", "abc123", datetime.now(UTC), "application/pdf")
    assert artifact.filename.endswith(".pdf")
    assert "foto-final" in artifact.filename
    assert artifact.org_link.startswith("[[artifact:")


def test_artifact_never_overwrites_existing_file(runtime_paths):
    now = datetime.now(UTC)
    publish_artifact(runtime_paths["artifacts"], "artifact:", b"one", "a.pdf", "same", now, "application/pdf")
    with pytest.raises(FileExistsError):
        publish_artifact(runtime_paths["artifacts"], "artifact:", b"two", "a.pdf", "same", now, "application/pdf")
