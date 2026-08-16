# mobile-org-capture

Personal Telegram bot that retains captures in a local filesystem queue and appends them as TODO
headings to an Org inbox file. Requires Python 3.11, `uv`, and systemd. No containers, no database,
no webhook — reception uses long polling only.

Once a capture is retained, ingestion never touches the network. A capture confirmed as received is
never lost; a retry may duplicate a heading, which is the intended trade-off.

## Configuration

All settings come from a systemd `EnvironmentFile` outside this repository.

| Variable | Meaning |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot credential from BotFather |
| `TELEGRAM_ALLOWED_CHAT_ID` | The only chat allowed to send captures |
| `CAPTURE_QUEUE_DIR` | Local root holding `pending/` and `done/`; must be outside the Syncthing tree |
| `ORG_INBOX_PATH` | Destination Org file |
| `ORG_ARTIFACTS_DIR` | Attachment directory inside the Org tree |
| `ORG_ARTIFACTS_LINK_PREFIX` | Org link abbreviation, e.g. `artifact:` |
| `CAPTURE_TIMEZONE` | IANA zone used for timestamps |
| `MAX_ATTACHMENT_BYTES` | Attachments above this are rejected before download |
| `CAPTURE_SWEEP_INTERVAL` | Seconds between ingestion sweeps |

## Deployment

Clone to the path referenced by `ExecStart` in `deploy/mobile-org-capture.service`, and run `uv sync`
as the same user the unit runs as — the service needs read access to the resulting `.venv`.

```sh
uv sync --frozen

# Queue directory, owned by the service user, outside the Syncthing tree
sudo install -d -o "$SERVICE_USER" -g "$SERVICE_USER" -m 700 /var/lib/mobile-org-capture

# Environment file; -D creates the parent directory
sudo install -D -m 600 deploy/mobile-org-capture.env.example \
    /etc/mobile-org-capture/mobile-org-capture.env

sudo install -m 644 deploy/mobile-org-capture.service \
    /etc/systemd/system/mobile-org-capture.service
sudo systemctl daemon-reload
sudo systemctl enable --now mobile-org-capture
```

Fill in `/etc/mobile-org-capture/mobile-org-capture.env` with the real token and chat ID. Never copy
secrets into this repository.

Only one process may consume updates for a given bot token. Stop any development instance before
starting the service, or use a separate bot for testing.

After a reboot or power loss, systemd restarts the bot and the startup sweep ingests any pending
manifests without network access.

## Emacs setup, per machine

Artifact links are written as `[[artifact:<filename>][<description>]]` rather than as filesystem
paths, so they keep resolving after the heading is refiled to another file. The abbreviation
resolves to a different absolute path on each machine, which is why it is configured per device
rather than stored in the link:

```elisp
(after! org
  (add-to-list 'org-link-abbrev-alist
               '("artifact" . "file:~/org/artifacts/%s")))
```

Adjust the path to where the Org tree lives on that machine. The abbreviation name must match
`ORG_ARTIFACTS_LINK_PREFIX` without its trailing colon.

## Syncthing setup, per machine

Attachments are downloaded to a temporary file in the same directory as their final path, which is
inside the replicated Org tree. Those temporaries must not propagate.

In the root of the shared Org folder, create `.stglobalignore`:

```
(?d)/artifacts/.*.tmp
```

And on every device, a `.stignore` containing one line:

```
#include .stglobalignore
```

`.stignore` is never synced between devices, but `.stglobalignore` is — so a new pattern is added
once and reaches every machine. The `#include` line still has to be created by hand on each new
device. Replace `artifacts` with the actual basename of `ORG_ARTIFACTS_DIR`.

## Usage

Send text, a URL, a photo, or a document from the authorized chat. The first line becomes the
heading title; remaining lines become the body. URLs are stored verbatim.

Two distinguishable replies arrive: one when the capture is durably retained, another when it has
been appended to the inbox. Receiving the first without the second means ingestion failed and the
capture is still queued.

`/pendientes` reports how many captures are retained but not yet ingested, and their titles.

## Development

```sh
uv sync
uv run pytest
uv run --python 3.11 pytest   # target runtime; development may use a newer interpreter
```

Tests use synthetic fixtures only. Never add real captures, tokens, chat IDs, or downloaded media to
the repository.

## Design documents

`specs/001-mobile-org-capture/` holds the specification, plan, research notes, data model, and the
Telegram contract. `.specify/memory/constitution.md` holds the invariants every change must respect.
