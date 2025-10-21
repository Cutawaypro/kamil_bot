import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from data.local_storage import save_audit
from data.storage import register_user
from utils.scheduler import schedule_follow_up


router = Router()

ADMIN_CONTACT = "@KamilTGMarketer"

AUDIT_INTRO_MESSAGE = (
    "Окей 👌\n"
    "Сейчас я проведу мини-аудит твоего Telegram-канала или Ads.\n"
    "Ответь на пару вопросов — и я покажу, где сгорает бюджет."
)

AUDIT_CONFIRMED_MESSAGE = (
    "✅ Ты записан на аудит!\n"
    "Мы свяжемся с тобой в ближайшее время через @KamilTGMarketer."
)

AUDIT_OPTIONS = [
    "Telegram Ads",
    "Канал и оформление",
    "Посевы",
    "Всё сразу",
]

GOAL_OPTIONS = [
    "Продажи",
    "Подписчики",
    "Вовлечение",
    "Другое",
]


class AuditStates(StatesGroup):
    waiting_for_audit_type = State()
    waiting_for_goal = State()
    waiting_for_link = State()


def audit_type_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=option)] for option in AUDIT_OPTIONS],
        resize_keyboard=True,
    )


def goal_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=option)] for option in GOAL_OPTIONS],
        resize_keyboard=True,
    )


@router.message(F.text == "🔍 Бесплатный аудит")
async def start_audit_flow(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AuditStates.waiting_for_audit_type)
    register_user(message.from_user.id, message.from_user.username)
    await message.answer(AUDIT_INTRO_MESSAGE)
    await message.answer(
        "Что ты хочешь проверить?",
        reply_markup=audit_type_keyboard(),
    )


@router.message(AuditStates.waiting_for_audit_type)
async def process_audit_type(message: Message, state: FSMContext) -> None:
    if message.text not in AUDIT_OPTIONS:
        await message.answer("Выбери вариант из списка — это поможет сфокусироваться.", reply_markup=audit_type_keyboard())
        return

    await state.update_data(audit_type=message.text)
    await state.set_state(AuditStates.waiting_for_goal)
    await message.answer("Какая цель рекламы?", reply_markup=goal_keyboard())


@router.message(AuditStates.waiting_for_goal)
async def process_goal(message: Message, state: FSMContext) -> None:
    if message.text not in GOAL_OPTIONS:
        await message.answer("Цель не распознал — выбери подходящую кнопку или «Другое».", reply_markup=goal_keyboard())
        return

    await state.update_data(goal=message.text)
    await state.set_state(AuditStates.waiting_for_link)
    await message.answer(
        "Вставь ссылку на свой канал или Ads-проект.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(AuditStates.waiting_for_link)
async def process_link(message: Message, state: FSMContext) -> None:
    link = message.text.strip()
    if not link:
        await message.answer("Ссылка нужна, чтобы я заглянул в проект. Поделись ей, пожалуйста.")
        return

    data = await state.get_data()
    answers = {
        "audit_type": data.get("audit_type"),
        "goal": data.get("goal"),
        "link": link,
    }

    username = message.from_user.username
    display_name = f"@{username}" if username else message.from_user.full_name or "Неизвестно"

    try:
        await asyncio.to_thread(
            save_audit,
            {
                "user_id": message.from_user.id,
                "username": display_name,
                "audit_type": answers["audit_type"],
                "goal": answers["goal"],
                "link": answers["link"],
            },
        )
    except Exception as exc:  # noqa: BLE001
        logging.exception("Failed to save audit request: %s", exc)

    try:
        await message.bot.send_message(
            ADMIN_CONTACT,
            "🆕 Новая заявка на аудит от {user}\nЦель: {goal}\nСсылка: {link}".format(
                user=display_name,
                goal=answers["goal"],
                link=answers["link"],
            ),
        )
    except Exception as exc:  # noqa: BLE001
        logging.exception("Failed to notify admin about audit request: %s", exc)

    try:
        await schedule_follow_up(
            bot=message.bot,
            user_id=message.from_user.id,
            username=display_name,
        )
    except Exception as exc:  # noqa: BLE001
        logging.exception("Failed to schedule follow-up for audit request: %s", exc)

    await message.answer(
        AUDIT_CONFIRMED_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    await state.clear()
