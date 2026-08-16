# Data Model: Captura móvil al inbox Org

## Configuration

| Setting | Meaning | Validation |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram bot credential | Required; loaded only from systemd `EnvironmentFile` |
| `TELEGRAM_ALLOWED_CHAT_ID` | Sole authorized chat identifier | Required integer; compare before processing the update |
| `CAPTURE_QUEUE_DIR` | Local root for `pending/` and `done/` manifests | Required existing local writable directory |
| `ORG_INBOX_PATH` | Final Org inbox file | Required local writable path |
| `ORG_ARTIFACTS_DIR` | Artifact directory inside the Org tree | Required local writable directory |
| `ORG_ARTIFACTS_LINK_PREFIX` | Org link abbreviation prefix | Required non-empty abbreviation ending in `:` |
| `CAPTURE_TIMEZONE` | IANA zone used in timestamps | Required valid IANA name |
| `MAX_ATTACHMENT_BYTES` | Maximum accepted attachment size | Required positive integer |
| `CAPTURE_SWEEP_INTERVAL` | Seconds between ingestion sweeps of `pending/` | Required positive integer; a sweep also runs at service start |

## Capture Manifest

One UTF-8 `.txt` manifest represents one accepted capture. Its filename is a normalized timestamp
plus a collision-resistant identifier. It is in `pending/` until the inbox append completes and is
then moved unchanged to `done/`.

| Field | Description | Validation |
|---|---|---|
| `capture_id` | Unique local identifier | Required; used in manifest and artifact names |
| `received_at` | Reception timestamp | Required; ISO 8601 with configured time zone and numeric offset |
| `telegram_message_id` | Telegram source message identifier | Required integer |
| `title` | First line of text or caption | Required; use `Sin título` when the first line is empty |
| `body` | Remaining lines after title | May be empty; preserve order and exact links |
| `artifacts` | Published attachment records | Zero or more; every referenced artifact must already exist |

The manifest is the durable boundary for receipt confirmation. It is not rewritten after
publication. A failure before publication receives no receipt confirmation; a failure after
publication leaves the manifest pending.

## Artifact

| Field | Description | Validation |
|---|---|---|
| `filename` | Normalized final filename | Timestamp-prefixed, includes `capture_id`, and never collides. When the Telegram message supplies a filename, it is normalized to ASCII with unsafe characters removed and its extension preserved. When it supplies none, as with compressed photos, the name is derived from `capture_id` and the extension inferred from the declared content type. |
| `local_path` | Absolute path in `ORG_ARTIFACTS_DIR` | Must be inside configured artifact directory |
| `org_link` | Link stored in heading | Uses `ORG_ARTIFACTS_LINK_PREFIX` plus filename, never a relative path |
| `size_bytes` | Downloaded size | Must not exceed `MAX_ATTACHMENT_BYTES` |

Artifact state is `temporary` -> `published`. Only `published` artifacts may be referenced by a
manifest. The binary is fully published before its referencing manifest.
An attachment whose declared size exceeds `MAX_ATTACHMENT_BYTES` is never downloaded.

## Ingestion State

State is derived entirely from manifest placement, so no database or separate persisted status
exists.

| State | Location | Meaning | Transition |
|---|---|---|---|
| Retained / pending | `pending/*.txt` | Receipt confirmation sent; not yet confirmed in inbox | Append heading, then rename to `done/` |
| Incorporated | `done/*.txt` | Heading append completed | Terminal; manifest remains retained |

If the process stops after the Org append but before the `done/` rename, retrying can create a
second heading. This is intentional and preferred to losing the capture.

## Org Heading

The ingester appends one complete TODO heading per manifest. It contains the capture reception
timestamp, title, body, and zero or more artifact abbreviation links. It never modifies prior
inbox bytes. The heading timestamp is `received_at`, not the later ingestion time.
