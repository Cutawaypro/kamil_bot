import logging
from datetime import datetime, timedelta
from typing import Optional

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data.config import get_config


scheduler = AsyncIOScheduler()


def start_scheduler(bot: Bot) -> None:
    """Ensure that the background scheduler is running."""
    if not scheduler.running:
        scheduler.start()


async def schedule_follow_up(bot: Bot, user_id: int, username: Optional[str]) -> None:
    """
    Планирует сообщение пользователю через указанное количество часов после аудита.
    """
    start_scheduler(bot)

    config = get_config()
    delay_hours = max(config.follow_up_delay_hours, 1)
    run_time = datetime.now() + timedelta(hours=delay_hours)

    try:
        scheduler.add_job(
            send_follow_up,
            trigger="date",
            run_date=run_time,
            args=[bot, user_id, username],
            misfire_grace_time=3600,
        )
    except Exception as exc:  # noqa: BLE001
        logging.exception("Failed to schedule follow-up message: %s", exc)


async def send_follow_up(bot: Bot, user_id: int, username: Optional[str]) -> None:
    text = (
        f"Хей 👋 {username or ''}\n"
        "Ты уже посмотрел рекомендации по своему каналу?\n"
        "Если нет — напомню, вот ссылка 📎\n\n"
        "Хочешь, я помогу уточнить, где именно можно улучшить кампанию?"
    )
    try:
        await bot.send_message(user_id, text)
    except Exception as exc:  # noqa: BLE001
        logging.exception("Failed to send follow-up message: %s", exc)
