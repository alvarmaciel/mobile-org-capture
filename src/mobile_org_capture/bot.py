"""Telegram boundary: authorize first, retain locally, then notify."""

from __future__ import annotations

from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from .artifacts import publish_artifact
from .capture import Capture
from .ingest import Ingester
from .settings import Settings
from .spool import Spool


class CaptureBot:
    def __init__(self, settings: Settings, spool: Spool, ingester: Ingester) -> None:
        self.settings = settings
        self.spool = spool
        self.ingester = ingester

    def authorized(self, update: Update) -> bool:
        message = update.effective_message
        return bool(message and message.chat_id == self.settings.telegram_allowed_chat_id)

    async def capture(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self.authorized(update):
            return
        message = update.effective_message
        assert message is not None
        received_at = datetime.now(self.settings.timezone)
        capture = Capture.create(message.text or message.caption, message.message_id, received_at)
        attachment = message.document or (message.photo[-1] if message.photo else None)
        oversized = False
        if attachment:
            size = getattr(attachment, "file_size", None)
            if size is not None and size > self.settings.max_attachment_bytes:
                oversized = True
                capture = capture.with_rejected_attachment(getattr(attachment, "file_name", "adjunto"))
            else:
                telegram_file = await context.bot.get_file(attachment.file_id)
                data = bytes(await telegram_file.download_as_bytearray())
                if len(data) > self.settings.max_attachment_bytes:
                    oversized = True
                    capture = capture.with_rejected_attachment(getattr(attachment, "file_name", "adjunto"))
                else:
                    artifact = publish_artifact(
                        self.settings.artifacts_dir,
                        self.settings.artifacts_link_prefix,
                        data,
                        getattr(attachment, "file_name", None),
                        capture.capture_id,
                        received_at,
                        getattr(attachment, "mime_type", None),
                    )
                    capture = capture.with_artifact(artifact)
        path = self.spool.publish(capture)
        await message.reply_text(f"Recibida y retenida: {capture.capture_id}")
        if oversized:
            await message.reply_text("Adjunto rechazado por tamaño; el texto fue retenido.")
        completed = await self.ingester.sweep()
        if capture.capture_id in completed:
            await message.reply_text(f"Incorporada al inbox: {capture.capture_id}")

    async def pending(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self.authorized(update):
            return
        message = update.effective_message
        assert message is not None
        titles = self.spool.pending_titles()
        response = f"Pendientes: {len(titles)}"
        if titles:
            response += "\n" + "\n".join(f"- {title}" for title in titles)
        await message.reply_text(response)


def build_application(settings: Settings, spool: Spool, ingester: Ingester) -> Application:
    boundary = CaptureBot(settings, spool, ingester)
    application = Application.builder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("pendientes", boundary.pending))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.Document.ALL, boundary.capture))
    return application
