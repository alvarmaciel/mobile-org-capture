# Telegram Bot Contract

## Authorization Boundary

Every incoming update is checked against `TELEGRAM_ALLOWED_CHAT_ID` before interpreting its text,
caption, media metadata, command, or attachment. Updates from any other chat receive no retention,
file creation, download, ingestion, or pending-status response.

## Accepted Captures

| Incoming Telegram message | Result after authorization |
|---|---|
| Text | First line becomes the TODO title; remaining lines are the body |
| Text containing URL | Stored verbatim; no URL title lookup or substitution |
| Photo with optional caption | Photo is published to artifacts first; caption is interpreted as title/body; heading contains an abbreviation link |
| Document with optional caption | Document is published to artifacts first; caption is interpreted as title/body; heading contains an abbreviation link |
| Attachment over `MAX_ATTACHMENT_BYTES` | Rejected with an error reply before download; if the message included text or a caption, that text is retained and ingested, and the resulting heading records the discarded attachment |

## Confirmations

| Event | Telegram response | Required condition |
|---|---|---|
| Receipt | `Recibida y retenida: <capture_id>` | All attachments, if any, and the capture manifest are durably published |
| Incorporation | `Incorporada al inbox: <capture_id>` | The complete TODO heading was durably appended and its manifest moved to `done/` |
| Incorporation failure | No incorporation confirmation; retry remains pending | Receipt was already sent; manifest remains in `pending/` |

Sending either reply is best effort and must not block local retention or ingestion. If the receipt
reply fails after retention, the capture remains pending and eligible for ingestion.

## Pending Command

`/pendientes` is available only to the authorized chat. It counts `.txt` manifests currently in
`CAPTURE_QUEUE_DIR/pending/` and replies with the count plus the title of each pending manifest.
It does not create or update persisted state.

## Operational Inputs

The systemd unit loads settings from an external `EnvironmentFile`. The file is not committed and
must contain the settings defined in [data-model.md](../data-model.md), including bot token and
authorized chat ID. The unit runs long polling only; no inbound HTTP endpoint is exposed.
