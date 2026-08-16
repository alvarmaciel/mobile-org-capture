# Quickstart: Validate captura móvil al inbox Org

## Prerequisites

- Raspberry Pi Linux host with systemd, Python 3.11, and an IANA time-zone database.
- Existing local Org tree, inbox file, artifact directory, and Org link abbreviation matching
  `ORG_ARTIFACTS_LINK_PREFIX`.
- A Telegram bot token and the sole permitted Telegram chat ID, stored in an external root-readable
  systemd environment file.
- Project dependencies installed with `uv sync --frozen` from the committed `uv.lock`.
## Configuration

Set the external environment file with `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_ID`,
`CAPTURE_QUEUE_DIR`, `ORG_INBOX_PATH`, `ORG_ARTIFACTS_DIR`, `ORG_ARTIFACTS_LINK_PREFIX`,
`CAPTURE_TIMEZONE`, `MAX_ATTACHMENT_BYTES`, and `CAPTURE_SWEEP_INTERVAL`. Ensure the service account can write all configured
local paths. Install and start the native systemd unit; confirm it is configured to restart after a
failure or reboot. Do not use Docker or a container runtime.

## Validation Scenarios

1. Send a two-line text note from the authorized chat. Confirm the receipt reply appears only after
   a manifest exists in `pending/`, then confirm the incorporation reply, appended TODO heading,
   configured-zone reception timestamp, and manifest in `done/`.
2. Send a URL. Verify its exact text is in the Org body and no network lookup changes its title.
3. Send a photo and a PDF with captions. Verify each binary appears under the artifact directory
   before its manifest references it, each filename is unique and timestamp-prefixed, and each Org
   heading uses the configured abbreviation link prefix rather than a relative path.
4. Make the inbox temporarily unwritable after a receipt confirmation. Verify `/pendientes` reports
   the affected capture and its title. Restore write access; verify local retry incorporates it. A
   duplicate heading is acceptable; a missing capture is not.
5. Restart the service while an accepted manifest is pending. Verify the service restarts under
   systemd and completes ingestion without needing network access after restart.
6. Send from an unauthorized chat and send an oversized attachment. Verify neither produces a queue
   manifest, artifact, inbox change, or incorporation confirmation.

## Automated Validation

Run the pytest suite using only synthetic fixtures. Include tests for authorization-before-work,
atomic publication ordering, append-only inbox behavior, interruption/retry behavior, pending count
and titles, timestamp zone formatting, link-abbreviation rendering, size rejection, and systemd
configuration rendering. Do not add real personal captures, tokens, chat IDs, or downloaded media
to the repository.

See [data-model.md](data-model.md) for state and configuration rules, and
[telegram-bot.md](contracts/telegram-bot.md) for the user-facing protocol.
