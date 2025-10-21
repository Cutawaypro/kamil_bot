from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Return a reply keyboard with the main navigation buttons."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Бесплатный аудит")],
            [KeyboardButton(text="📚 Гайды и материалы")],
            [KeyboardButton(text="💬 Задать вопрос")],
            [KeyboardButton(text="🌐 Визитка / сайт")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери раздел",
    )


def contact_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Написать Камилю",
                    url="https://t.me/KamilTGMarketer",
                )
            ]
        ]
    )
