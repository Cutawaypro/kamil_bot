import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from data.config import get_config
from handlers.admin import router as admin_router
from handlers.audit import router as audit_router
from handlers.contact import router as contact_router
from handlers.guides import router as guides_router
from handlers.site import router as site_router
from handlers.start import router as start_router
from utils.scheduler import start_scheduler


async def start_web_server():
    """Фиктивный сервер для Render, чтобы он видел открытый порт."""
    async def handle(request):
        return web.Response(text="Bot is alive!")

    app = web.Application()
    app.add_routes([web.get("/", handle)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()


async def main():
    logging.basicConfig(level=logging.INFO)
    config = get_config()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    start_scheduler(bot)

    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(audit_router)
    dp.include_router(guides_router)
    dp.include_router(contact_router)
    dp.include_router(site_router)

    # Запускаем веб-сервер и polling параллельно
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )


if __name__ == "__main__":
    asyncio.run(main())
