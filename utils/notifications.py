import logging
from typing import Dict

from aiogram import Bot


async def notify_admin(bot: Bot, admin_username: str, audit_data: Dict[str, str]) -> None:
    """
    Отправляет админу сообщение о новой заявке.
    Формат:
    🆕 Новый аудит!
    Пользователь: @username
    Тип: Telegram Ads
    Цель: Подписчики
    Ссылка: ...
    """
    if not admin_username:
        logging.warning("Admin username is empty; cannot send notification.")
        return

    message_text = (
        "🆕 Новый аудит!\n"
        f"Пользователь: {audit_data.get('user', 'Неизвестно')}\n"
        f"Тип: {audit_data.get('audit_type', '—')}\n"
        f"Цель: {audit_data.get('goal', '—')}\n"
        f"Ссылка: {audit_data.get('link', '—')}"
    )

    try:
        await bot.send_message(chat_id=admin_username, text=message_text)
    except Exception as exc:  # noqa: BLE001
        logging.exception("Failed to notify admin about new audit: %s", exc)
        print(f"[ADMIN NOTICE - FALLBACK]\n{message_text}")
