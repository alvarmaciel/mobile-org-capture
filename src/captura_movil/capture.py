"""Immutable capture manifest types and message normalization."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class Artifact:
    filename: str
    size_bytes: int
    org_link: str


@dataclass(frozen=True)
class Capture:
    capture_id: str
    received_at: str
    telegram_message_id: int
    title: str
    body: str
    artifacts: tuple[Artifact, ...] = ()
    rejected_attachments: tuple[str, ...] = ()

    @classmethod
    def create(cls, text: str | None, message_id: int, received_at: datetime) -> "Capture":
        lines = (text or "").splitlines()
        title = lines[0].strip() if lines else ""
        return cls(
            capture_id=uuid4().hex,
            received_at=received_at.isoformat(),
            telegram_message_id=message_id,
            title=title or "Sin título",
            body="\n".join(lines[1:]),
        )

    def with_artifact(self, artifact: Artifact) -> "Capture":
        return replace(self, artifacts=self.artifacts + (artifact,))

    def with_rejected_attachment(self, description: str) -> "Capture":
        return replace(self, rejected_attachments=self.rejected_attachments + (description,))

    def to_dict(self) -> dict[str, object]:
        return {
            "capture_id": self.capture_id,
            "received_at": self.received_at,
            "telegram_message_id": self.telegram_message_id,
            "title": self.title,
            "body": self.body,
            "artifacts": [asdict(item) for item in self.artifacts],
            "rejected_attachments": list(self.rejected_attachments),
        }

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "Capture":
        return cls(
            capture_id=str(value["capture_id"]),
            received_at=str(value["received_at"]),
            telegram_message_id=int(value["telegram_message_id"]),
            title=str(value["title"]),
            body=str(value["body"]),
            artifacts=tuple(Artifact(**item) for item in value.get("artifacts", [])),  # type: ignore[arg-type]
            rejected_attachments=tuple(str(item) for item in value.get("rejected_attachments", [])),
        )
