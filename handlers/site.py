from aiogram import F, Router
from aiogram.types import Message

from data import texts


router = Router()


@router.message(F.text == "🌐 Визитка / сайт")
async def handle_site(message: Message) -> None:
    await message.answer(texts.SITE_MESSAGE)
