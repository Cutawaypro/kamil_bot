import asyncio
import logging
import threading
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


# --- фиктивный web-сервер для Render ---
async def handle(request):
    return web.Response(text="Bot is alive!")

def run_web_server():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    web.run_app(app, host="0.0.0.0", port=10000)


# --- основной бот ---
async def main() -> None:
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

    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запускаем фиктивный сервер в отдельном потоке
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
