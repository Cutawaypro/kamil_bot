from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from data import texts
from data.storage import register_user
from utils.keyboard import main_menu_keyboard


router = Router()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    username = message.from_user.username or message.from_user.full_name or ""
    register_user(message.from_user.id, message.from_user.username)
    await message.answer(texts.WELCOME_MESSAGE, reply_markup=main_menu_keyboard())
