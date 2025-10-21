from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.keyboard import main_menu_keyboard


router = Router()

SECTION_BASICS = "guides:basics"
SECTION_BASICS_BACK = "guides:basics_back"
SECTION_CASES = "guides:cases"
SECTION_CASES_BACK = "guides:cases_back"
SECTION_AUTOMATION = "guides:automation"
SECTION_AUTOMATION_BACK = "guides:automation_back"
SECTION_BACK = "guides:back"

SECTION_ITEMS = {
    "1": [
        {
            "label": "1️⃣ Что такое Telegram Ads и почему он не работает",
            "url": "https://telegra.ph/1-post-1-razdel-10-20",
        },
        {
            "label": "2️⃣ Как выбрать цель кампании и не сжечь бюджет",
            "url": "https://telegra.ph/2-post-1-razdel-10-20",
        },
        {
            "label": "3️⃣ Пиксель в Telegram: зачем он и как понять, что он вообще работает",
            "url": "https://telegra.ph/3-post-1-razdel-10-20",
        },
        {
            "label": "4️⃣ Как считать результат рекламы: CTR ≠ прибыль",
            "url": "https://telegra.ph/4-post-1-razdel-10-20",
        },
        {
            "label": "5️⃣ Рекламный текст, который кликают",
            "url": "https://telegra.ph/5-post-1-razdel-10-20",
        },
        {
            "label": "6️⃣ Мини-чеклист перед запуском Ads",
            "url": "https://telegra.ph/6-post-1-razdel-10-20",
        },
    ],
    "2": [
        {
            "label": "1️⃣ ТОП-5 ошибок, из-за которых Ads не окупается",
            "url": "https://telegra.ph/1-post-2-razdel-10-20",
        },
        {
            "label": "2️⃣ Кейс: как я снизил CPL с 480 ₽ до 190 ₽ — по шагам",
            "url": "https://telegra.ph/2-post-2-razdel-10-20",
        },
        {
            "label": "3️⃣ Почему CTR 15% — это не успех (и что считать вместо него)",
            "url": "https://telegra.ph/3-post-2-razdel-10-20",
        },
        {
            "label": "4️⃣ Факап: реклама шла, лидов нет",
            "url": "https://telegra.ph/4-post-2-razdel-10-20",
        },
        {
            "label": "5️⃣ Кейс клиента: ROI ×4 без увеличения бюджета",
            "url": "https://telegra.ph/5-post-2-razdel-10-20",
        },
        {
            "label": "6️⃣ 3 сигнала, что подрядчик тратит твои деньги впустую",
            "url": "https://telegra.ph/6-post-2-razdel-10-20",
        },
    ],
    "3": [
        {
            "label": "1️⃣ Как не тратить 2 часа в день на отчёты",
            "url": "https://telegra.ph/1-post-3-razdel-10-20",
        },
        {
            "label": "2️⃣ Боты, которые экономят бюджет (и нервы)",
            "url": "https://telegra.ph/2-post-3-razdel-10-20",
        },
        {
            "label": "3️⃣ Telegram Ads + Google Sheets: простая сквозная аналитика",
            "url": "https://telegra.ph/3-post-3-razdel-10-20",
        },
        {
            "label": "4️⃣ Сценарий “воронки на автопилоте”",
            "url": "https://telegra.ph/4-post-3-razdel-10-20",
        },
        {
            "label": "5️⃣ Автоматизация лидогенерации через Ads + бот",
            "url": "https://telegra.ph/5-post-3-razdel-10-20",
        },
        {
            "label": "6️⃣ Инструменты для Telegram-маркетолога: must-have 2025",
            "url": "https://telegra.ph/6-post-3-razdel-10-20",
        },
    ],
}


def guides_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Раздел 1 · Основы Telegram Ads", callback_data=SECTION_BASICS)
    builder.button(text="Раздел 2 · Ошибки и кейсы", callback_data=SECTION_CASES)
    builder.button(text="Раздел 3 · Автоматизация", callback_data=SECTION_AUTOMATION)
    builder.button(text="Назад в меню", callback_data=SECTION_BACK)
    builder.adjust(1)
    return builder.as_markup()


def _build_section_keyboard(section_id: str, back_callback: str):
    builder = InlineKeyboardBuilder()
    for item in SECTION_ITEMS.get(section_id, []):
        builder.button(text=item["label"], url=item["url"])
    builder.button(text="Назад к разделам", callback_data=back_callback)
    builder.adjust(1)
    return builder.as_markup()


def basics_section_keyboard():
    return _build_section_keyboard("1", SECTION_BASICS_BACK)


def cases_section_keyboard():
    return _build_section_keyboard("2", SECTION_CASES_BACK)


def automation_section_keyboard():
    return _build_section_keyboard("3", SECTION_AUTOMATION_BACK)


@router.message(F.text == "📚 Гайды и материалы")
async def handle_guides(message: Message) -> None:
    await message.answer(
        "Загляни в подборку материалов — выбери раздел 👇",
        reply_markup=guides_menu_keyboard(),
    )


@router.callback_query(F.data == SECTION_BASICS)
async def show_basics(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "Раздел 1 · Основы Telegram Ads",
        reply_markup=basics_section_keyboard(),
    )


@router.callback_query(F.data == SECTION_BASICS_BACK)
async def back_to_guides(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "Загляни в подборку материалов — выбери раздел 👇",
        reply_markup=guides_menu_keyboard(),
    )


@router.callback_query(F.data == SECTION_CASES)
async def show_cases(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "Раздел 2 · Ошибки и кейсы",
        reply_markup=cases_section_keyboard(),
    )


@router.callback_query(F.data == SECTION_CASES_BACK)
async def back_to_guides_from_cases(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "Загляни в подборку материалов — выбери раздел 👇",
        reply_markup=guides_menu_keyboard(),
    )


@router.callback_query(F.data == SECTION_AUTOMATION)
async def show_automation(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "Раздел 3 · Автоматизация",
        reply_markup=automation_section_keyboard(),
    )


@router.callback_query(F.data == SECTION_AUTOMATION_BACK)
async def back_to_guides_from_automation(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "Загляни в подборку материалов — выбери раздел 👇",
        reply_markup=guides_menu_keyboard(),
    )


@router.callback_query(F.data == SECTION_BACK)
async def go_back(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "Возвращаю в главное меню, выбирай следующий шаг ⚡️",
        reply_markup=main_menu_keyboard(),
    )
