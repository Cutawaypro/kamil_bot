import asyncio
import logging

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


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = get_config()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    # запускаем планировщик (follow-up + дайджест)
    start_scheduler(bot)

    # подключаем все обработчики
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(audit_router)
    dp.include_router(guides_router)
    dp.include_router(contact_router)
    dp.include_router(site_router)

    # запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
