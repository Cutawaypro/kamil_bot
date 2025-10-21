from aiogram import F, Router
from aiogram.types import Message

from data import texts
from utils.keyboard import contact_keyboard


router = Router()


@router.message(F.text == "💬 Задать вопрос")
async def handle_contact(message: Message) -> None:
    await message.answer(texts.CONTACT_MESSAGE, reply_markup=contact_keyboard())
