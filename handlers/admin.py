import asyncio
import logging
from datetime import datetime
from typing import List, Tuple

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.config import get_config
from data.local_storage import load_audits, remove_audit
from data.storage import get_known_user_ids, register_user
from utils.keyboard import main_menu_keyboard


router = Router()

_CONFIG = get_config()
_ADMIN_USERNAME = (_CONFIG.admin_username or "").lstrip("@").lower()

ADMIN_MENU_REQUESTS = "admin:requests"
ADMIN_MENU_STATS = "admin:stats"
ADMIN_MENU_BROADCAST = "admin:broadcast"
ADMIN_MENU_BACK = "admin:back"
ADMIN_BROADCAST_CONFIRM = "admin:broadcast_confirm"
ADMIN_BROADCAST_CANCEL = "admin:broadcast_cancel"
ADMIN_RESOLVE_PREFIX = "admin:resolve:"


class AdminBroadcastStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_confirmation = State()


def admin_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Заявки", callback_data=ADMIN_MENU_REQUESTS)
    builder.button(text="📊 Статистика", callback_data=ADMIN_MENU_STATS)
    builder.button(text="📢 Рассылка", callback_data=ADMIN_MENU_BROADCAST)
    builder.button(text="🔙 Назад", callback_data=ADMIN_MENU_BACK)
    builder.adjust(1)
    return builder.as_markup()


def _is_authorized(username: str | None) -> bool:
    if not _ADMIN_USERNAME:
        logging.warning("ADMIN_USERNAME is not configured; denying admin access.")
        return False
    return (username or "").lower() == _ADMIN_USERNAME


def _format_timestamp(raw: str) -> str:
    try:
        dt = datetime.fromisoformat(raw)
    except (ValueError, TypeError):
        return raw or "Не указан"
    return dt.strftime("%d.%m %H:%M")


async def _load_recent_audits(limit: int = 5) -> List[Tuple[int, dict]]:
    audits = await asyncio.to_thread(load_audits)
    indexed = list(enumerate(audits))
    recent = indexed[-limit:]
    recent.reverse()
    return recent


@router.message(Command("admin"))
async def admin_entry(message: Message, state: FSMContext) -> None:
    if not _is_authorized(message.from_user.username):
        await message.answer("⛔ Доступ запрещён.")
        return

    register_user(message.from_user.id, message.from_user.username)
    await state.clear()
    await message.answer("Привет! Что делаем дальше?", reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == ADMIN_MENU_REQUESTS)
async def show_recent_requests(callback: CallbackQuery) -> None:
    if not _is_authorized(callback.from_user.username):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return

    await callback.answer()
    recent = await _load_recent_audits()

    if not recent:
        await callback.message.answer("Нет новых заявок 👌", reply_markup=admin_menu_keyboard())
        return

    lines = ["📋 Последние заявки:"]
    keyboard = InlineKeyboardBuilder()

    for index, entry in recent:
        timestamp = _format_timestamp(entry.get("timestamp", ""))
        username = entry.get("username") or "Без ника"
        audit_type = entry.get("audit_type") or "—"
        goal = entry.get("goal") or "—"
        link = entry.get("link") or "—"
        lines.append(
            f"{timestamp} — {username}\n"
            f"Тип: {audit_type}\n"
            f"Цель: {goal}\n"
            f"Ссылка: {link}"
        )
        keyboard.button(
            text=f"✅ Разобрано — {username}",
            callback_data=f"{ADMIN_RESOLVE_PREFIX}{index}",
        )

    keyboard.button(text="🔙 Назад", callback_data=ADMIN_MENU_BACK)
    keyboard.adjust(1)

    await callback.message.answer("\n\n".join(lines), reply_markup=keyboard.as_markup())


@router.callback_query(F.data == ADMIN_MENU_STATS)
async def show_stats(callback: CallbackQuery) -> None:
    if not _is_authorized(callback.from_user.username):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return

    await callback.answer()
    audits = await asyncio.to_thread(load_audits)
    recipients = list(get_known_user_ids())

    text = (
        "📊 Статистика:\n"
        f"📥 Всего заявок: {len(audits)}\n"
        f"📬 В очереди: {len(audits)}\n"
        f"👥 Пользователей для рассылки: {len(recipients)}"
    )

    await callback.message.answer(text, reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == ADMIN_MENU_BROADCAST)
async def prompt_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_authorized(callback.from_user.username):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return

    await callback.answer()
    await state.set_state(AdminBroadcastStates.waiting_for_text)
    await callback.message.answer("Введите текст рассылки.")


@router.message(AdminBroadcastStates.waiting_for_text)
async def receive_broadcast_text(message: Message, state: FSMContext) -> None:
    if not _is_authorized(message.from_user.username):
        await message.answer("⛔ Доступ запрещён.")
        await state.clear()
        return

    if not message.text:
        await message.answer("Нужен текстовый ответ для рассылки.")
        return

    recipients = list(get_known_user_ids())
    if not recipients:
        await message.answer("Нет получателей для рассылки.")
        await state.clear()
        return

    await state.update_data(
        broadcast_text=message.text,
        recipients=recipients,
    )
    await state.set_state(AdminBroadcastStates.waiting_for_confirmation)

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Отправить", callback_data=ADMIN_BROADCAST_CONFIRM)
    builder.button(text="❌ Отменить", callback_data=ADMIN_BROADCAST_CANCEL)
    builder.adjust(2)

    await message.answer(
        f"Отправить рассылку {len(recipients)} пользователям?",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(
    AdminBroadcastStates.waiting_for_confirmation,
    F.data == ADMIN_BROADCAST_CONFIRM,
)
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_authorized(callback.from_user.username):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        await state.clear()
        return

    await callback.answer()
    data = await state.get_data()
    text = data.get("broadcast_text")
    recipients = data.get("recipients", [])

    if not text or not recipients:
        await callback.message.edit_reply_markup()
        await callback.message.answer("Нет данных для рассылки, начните заново.", reply_markup=admin_menu_keyboard())
        await state.clear()
        return

    try:
        await callback.message.edit_reply_markup()
    except Exception:
        pass

    total = len(recipients)
    sent = 0
    for index, user_id in enumerate(recipients, start=1):
        try:
            await callback.bot.send_message(user_id, text)
            sent += 1
        except Exception:  # noqa: BLE001
            logging.exception("Failed to send broadcast to %s", user_id)

        if index < total:
            await asyncio.sleep(2)
            if index % 30 == 0:
                await asyncio.sleep(60)

    await callback.message.answer(
        f"✅ Рассылка завершена. Успешно отправлено {sent} / {total}.",
        reply_markup=admin_menu_keyboard(),
    )
    await state.clear()


@router.callback_query(
    AdminBroadcastStates.waiting_for_confirmation,
    F.data == ADMIN_BROADCAST_CANCEL,
)
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_authorized(callback.from_user.username):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        await state.clear()
        return

    await callback.answer("Отменено.")
    try:
        await callback.message.edit_reply_markup()
    except Exception:
        pass
    await callback.message.answer("Рассылка отменена.", reply_markup=admin_menu_keyboard())
    await state.clear()


@router.callback_query(F.data.startswith(ADMIN_RESOLVE_PREFIX))
async def resolve_request(callback: CallbackQuery) -> None:
    if not _is_authorized(callback.from_user.username):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return

    payload = callback.data[len(ADMIN_RESOLVE_PREFIX) :]
    try:
        index = int(payload)
    except ValueError:
        await callback.answer()
        return

    await asyncio.to_thread(remove_audit, index)
    await callback.answer("Готово!")

    recent = await _load_recent_audits()
    if not recent:
        await callback.message.edit_text("Нет новых заявок 👌", reply_markup=admin_menu_keyboard())
        return

    lines = ["📋 Последние заявки:"]
    keyboard = InlineKeyboardBuilder()
    for idx, entry in recent:
        timestamp = _format_timestamp(entry.get("timestamp", ""))
        username = entry.get("username") or "Без ника"
        audit_type = entry.get("audit_type") or "—"
        goal = entry.get("goal") or "—"
        link = entry.get("link") or "—"
        lines.append(
            f"{timestamp} — {username}\n"
            f"Тип: {audit_type}\n"
            f"Цель: {goal}\n"
            f"Ссылка: {link}"
        )
        keyboard.button(
            text=f"✅ Разобрано — {username}",
            callback_data=f"{ADMIN_RESOLVE_PREFIX}{idx}",
        )

    keyboard.button(text="🔙 Назад", callback_data=ADMIN_MENU_BACK)
    keyboard.adjust(1)

    await callback.message.edit_text("\n\n".join(lines), reply_markup=keyboard.as_markup())


@router.callback_query(F.data == ADMIN_MENU_BACK)
async def admin_back(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_authorized(callback.from_user.username):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return

    await callback.answer()
    await state.clear()
    await callback.message.answer(
        "Возвращаю в главное меню, выбирай следующий шаг ⚡️",
        reply_markup=main_menu_keyboard(),
    )
