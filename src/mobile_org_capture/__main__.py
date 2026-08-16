"""Native systemd entry point."""

from __future__ import annotations

import asyncio

from .bot import build_application
from .ingest import Ingester
from .settings import Settings
from .spool import Spool


async def run() -> None:
    settings = Settings.from_environment()
    spool = Spool(settings.queue_dir)
    ingester = Ingester(spool, settings.inbox_path)
    application = build_application(settings, spool, ingester)
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=["message"])
    try:
        while True:
            await ingester.sweep()
            await asyncio.sleep(settings.sweep_interval)
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
