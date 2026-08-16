from __future__ import annotations

from datetime import UTC, datetime

from captura_movil.artifacts import publish_artifact


def test_fifty_artifacts_are_published_without_temporary_files(runtime_paths):
    for number in range(50):
        artifact = publish_artifact(runtime_paths["artifacts"], "artifact:", b"image", f"photo-{number}.jpg", f"id{number}", datetime.now(UTC), "image/jpeg")
        assert (runtime_paths["artifacts"] / artifact.filename).exists()
        assert artifact.org_link.startswith("[[artifact:")
    assert list(runtime_paths["artifacts"].glob("*.tmp")) == []
