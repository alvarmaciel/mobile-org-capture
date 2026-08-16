# Implementation Plan: Captura móvil al inbox Org

**Branch**: `001-mobile-org-capture` | **Date**: 2026-08-15 | **Spec**:
[spec.md](spec.md)

## Summary

Implement a Python Telegram bot that accepts captures only from the configured chat ID by long
polling. It retains each accepted capture as an atomically published text manifest in a local
filesystem queue, sends the receipt confirmation, and then locally appends a TODO heading to the
configured Org inbox. Attachments are durably saved in the Org artifact directory before their
manifest is published. Successfully ingested manifests move to `done/` and remain there.

## Technical Context

**Language/Version**: Python 3.11 (system interpreter on Raspberry Pi OS)

**Primary Dependencies**: `python-telegram-bot` 22.8 for long polling and Telegram file download;
`pytest` for tests; Python standard library for filesystem, time zone, and process operations. Dependencies are declared in `pyproject.toml` and locked in `uv.lock`, managed with uv.

**Storage**: Local filesystem only: queue manifests under `CAPTURE_QUEUE_DIR`, `done/` manifests,
the configured `ORG_INBOX_PATH`, and an artifact directory inside the Org tree

**Testing**: pytest with synthetic message, attachment, filesystem, and time-zone fixtures; no
personal captures or secrets in the repository

**Target Platform**: Raspberry Pi running a supported Linux distribution with systemd

**Project Type**: Single Python bot/service

**Performance Goals**: No latency targets are specified. Pending status is computed by counting
queue files in a single Telegram request.

**Constraints**: No web framework, database, Docker, containers, or webhook. Telegram is used only
for reception and user notifications. Long polling is the sole reception method. The post-receipt
path must run without network access. All timestamps use the configured IANA time zone. Secrets are
loaded only through systemd `EnvironmentFile` outside the repository.
Org headings reference artifacts through an Org link abbreviation (`[[artifact:<name>][<name>]]`)
resolved per machine, never a relative or absolute path, so links survive refiling to other files.
Ingestion runs independently of message reception: a sweep at service start plus a periodic sweep.

**Scale/Scope**: One authorized Telegram chat and one Raspberry Pi; one queue manifest per capture;
the inbox file is append-only; received manifests are never deleted by the service.

## Constitution Check

| Principle | Design response | Gate |
|---|---|---|
| I. Preserve confirmed captures | Send receipt confirmation only after the manifest is locally durable. Manifests whose ingestion failed remain in `pending/`; retries may duplicate an Org heading but never discard the manifest. | PASS |
| II. Atomically publish files | Every manifest and artifact uses a temporary file in its final directory, flushes and fsyncs it, then atomically renames it. The final directory is fsynced after rename. | PASS |
| III. Append-only Org destination | The ingester opens the configured inbox only to append a complete heading; it never sorts, rewrites, or deletes existing content. | PASS |
| IV. Interruptible, idempotent ingestion | A manifest moves to `done/` only after the append has completed durably. An interruption before that leaves it pending; a retry can append again. | PASS |
| V. Authorize before processing | The Telegram update sender chat ID is compared to `TELEGRAM_ALLOWED_CHAT_ID` before parsing, downloading, creating files, or queuing a capture. | PASS |
| VI. Network-free ingestion | The ingester consumes only local manifests and local artifacts. Telegram communication is confined to receipt/notification and the pre-retention reception phase; failed notifications cannot block ingestion. | PASS |

**Post-design re-check**: PASS. The queue, artifact, inbox, and `done/` paths are all local paths.
No design element requires network access after an accepted manifest is published.

## Ingestion Scheduling
Ingestion is not tied to message reception. The service performs a sweep of the queue directory at
startup and then at a fixed interval defined by `CAPTURE_SWEEP_INTERVAL`. A manifest retained
during a crash or power loss is therefore ingested on the next sweep without requiring a new
capture. Sweeps are serialized: a sweep never starts while another is running.
## Project Structure

### Documentation (this feature)

```text
specs/001-mobile-org-capture/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── telegram-bot.md
└── tasks.md                 # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
src/captura_movil/
├── __main__.py              # Service entry point
├── bot.py                   # Telegram polling, authorization, commands, notifications
├── capture.py               # Message normalization and manifest construction
├── spool.py                 # Atomic manifest publication, enumeration, and done moves
├── ingest.py                # Local artifact-to-Org ingestion workflow
├── org.py                   # TODO heading rendering and append-only write
├── artifacts.py             # Attachment naming and atomic local publication
└── settings.py               # Required environment validation and IANA time zone

tests/
├── unit/
├── integration/
└── fixtures/

deploy/
└── captura-movil.service    # Native systemd unit; no environment secrets

pyproject.toml               # Project metadata, dependencies, requires-python = ">=3.11"
uv.lock                      # Fully resolved, hashed lock file (committed)
```

**Structure Decision**: Use one installable Python service package. The bot owns the network
boundary; the queue and ingester remain separately testable local components, ensuring retries and
systemd restarts do not require Telegram connectivity to complete ingestion.

## Dependency Management
Declare direct dependencies in `pyproject.toml`: `python-telegram-bot==22.8` for production and
`pytest` in a dev dependency group. Commit `uv.lock`, which uv resolves with hashes. Deploy with
`uv sync --frozen`, which fails rather than silently updating the lock. Upgrade intentionally by
editing `pyproject.toml`, running `uv lock`, reviewing the diff, and running the synthetic pytest
suite. No packages are installed at service startup.

## Deployment Design
The service runs as a native systemd unit with `Restart=always` and `RestartSec=10`, enabled with
`systemctl enable` so it starts at boot after a power loss. `ExecStart` points to the absolute path
of the entry point inside the uv-managed `.venv`, not to `uv run`, so startup is deterministic
without a shell or user PATH. The unit uses `EnvironmentFile=` pointing to a root-readable,
deployment-local file outside this repository, containing at least `TELEGRAM_BOT_TOKEN` and
`TELEGRAM_ALLOWED_CHAT_ID`; it also supplies the queue directory, inbox path, artifact directory,
Org link abbreviation prefix, sweep interval, time zone, and maximum attachment size. No Dockerfile,
container runtime, or web server is used.
## Complexity Tracking

No constitutional violations require justification.
