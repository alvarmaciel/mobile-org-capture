# Research: Captura móvil al inbox Org

## Telegram client library

**Decision**: Use `python-telegram-bot` 22.8 with its polling runtime.

**Rationale**: The official library documentation describes it as a pure-Python asynchronous
interface, compatible with Python 3.10+, with an application polling method and message handlers
for text, photos, and documents. It fits a single long-running bot without adding a web framework.
Version 22.8 requires only `httpx` transitively for its default network backend.

**Alternatives considered**:

- Calling the Telegram Bot API directly with an HTTP client: rejected because message routing,
  polling lifecycle, typed update handling, and file download would be reimplemented.
- `aiogram`: rejected because the selected library already satisfies the narrow requirement with a
  simpler dependency decision for this single-user service.

## Long polling and restart behavior

**Decision**: Use long polling exclusively and configure the bot to receive only message updates.
Do not configure a webhook. Start it under systemd with failure restart enabled.

**Rationale**: Telegram documents `getUpdates` as the long-polling mechanism and states it cannot
operate while a webhook is configured. Telegram retains incoming updates for up to 24 hours; on a
restart, polling resumes reception. Systemd restart covers process failure and boot after a power
cut. The bot must not acknowledge a capture until its local manifest is durable.

**Alternatives considered**:

- Webhook: rejected by the stated requirement and would require an inbound web service.
- A timer-triggered polling job: rejected because it increases capture latency and adds lifecycle
  complexity without improving durability.

## Durable queue and atomic publication

**Decision**: Represent each capture as one UTF-8 `.txt` manifest in `CAPTURE_QUEUE_DIR/pending/`.
Write all final files through a temporary sibling, flush and fsync the file, atomically rename it,
then fsync the containing directory. Move successful manifests to `CAPTURE_QUEUE_DIR/done/` using an
atomic same-filesystem rename; never delete them.

**Rationale**: A directory scan supplies the pending count without a database or side state. A
manifest is visible to the ingester only after full publication. Python documents `os.fsync` for
forcing file data to disk; the additional directory fsync makes the rename durable on Linux. The
same-directory temporary file satisfies the constitutional atomic-publication rule.

**Alternatives considered**:

- SQLite or a broker: rejected because the required queue semantics are one file per capture and no
  database is permitted.
- Directly appending Telegram content to Org: rejected because a power failure could lose the
  confirmed capture and there would be no retry record.

## Attachment ordering and Org links

**Decision**: Download each accepted attachment to a temporary file inside `ORG_ARTIFACTS_DIR`,
fsync and rename it to its unique normalized timestamp-prefixed final name, then publish the text
manifest that references the artifact. Render its Org link using `ORG_ARTIFACTS_LINK_PREFIX`, an Org
link abbreviation configured by the user, not a relative filesystem path.

**Rationale**: A manifest never references an artifact that has not been completely published.
Timestamp prefix plus a collision-resistant capture identifier supplies unique names without
overwriting existing artifacts. An Org link abbreviation survives placement and replication choices
outside this service.

**Alternatives considered**:

- Save attachments after publishing the manifest: rejected because the ingester could create a
  broken link.
- Relative links: rejected by the stated requirement.

## Time zones and dependencies

**Decision**: Require `CAPTURE_TIMEZONE` as a valid IANA time-zone name. Format timestamps from the
capture reception moment with numeric UTC offset in both manifest and Org heading. Use Python's
standard `zoneinfo`; do not add a time-zone library.

**Rationale**: An explicit configured zone prevents ambiguous timestamps and makes test fixtures
deterministic. The Raspberry Pi Linux image must provide the IANA zoneinfo database.

**Alternatives considered**:

- Host-local implicit time zone: rejected because deployments and tests could silently differ.
- UTC-only headings: rejected because the request requires an explicit zone meaningful to the user.

## Secret handling and repeatable installation

**Decision**: Place tokens and chat IDs only in a systemd `EnvironmentFile` outside the repository.
Declare dependencies in `pyproject.toml`, commit the `uv.lock` file uv resolves with hashes, and
deploy with `uv sync --frozen` against the system Python 3.11 interpreter.

**Rationale**: Systemd injects runtime configuration without storing secrets in source control.
A committed lock file makes deployments reproducible and lets review focus on intentional
dependency changes. `uv sync --frozen` fails instead of silently updating the lock, so an
unattended restart cannot change the installed set. Using the distribution interpreter keeps
security updates on the system package manager rather than on a separately managed runtime.

**Alternatives considered**:

- Committed `.env`: rejected because it risks secret disclosure.
- Unpinned `pip install` during boot: rejected because an unattended restart must not fetch or
  change dependencies.
- `pip-tools` with `requirements.in`/`requirements.txt`: rejected because uv covers resolution,
  hashing, and environment creation with fewer moving parts.
- A uv-managed standalone interpreter: rejected because this service needs no feature beyond
  Python 3.11 and the system interpreter receives distribution security updates.
