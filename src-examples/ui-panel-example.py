"""
Пример реализации концепции Persistent UI Panel (Интерфейс «одного сообщения»).
Данный паттерн позволяет минимизировать количество системных сообщений в чате 
и создать ощущение цельного приложения внутри Telegram.
"""

import logging
from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Настройка логера для демонстрации
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

def get_main_menu_keyboard():
    """Создает клавиатуру главного меню."""
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📷 Фото-ретушь", callback_data="nav_photo"))
    builder.row(types.InlineKeyboardButton(text="🎬 Видео-генерация", callback_data="nav_video"))
    builder.row(types.InlineKeyboardButton(text="👤 Личный кабинет", callback_data="nav_profile"))
    builder.row(types.InlineKeyboardButton(text="❓ Помощь", callback_data="nav_help"))
    return builder.as_markup()

async def update_persistent_panel(
    event: types.CallbackQuery | types.Message, 
    text: str, 
    reply_markup: types.InlineKeyboardMarkup
):
    """
    Универсальный метод обновления интерфейсной панели.
    Если передан CallbackQuery — редактирует старое сообщение.
    Если передан Message — отправляет новое (используется при первом входе).
    """
    if isinstance(event, types.CallbackQuery):
        try:
            await event.message.edit_text(text=text, reply_markup=reply_markup)
        except Exception as e:
            logger.warning(f"Failed to edit message: {e}")
            await event.message.answer(text=text, reply_markup=reply_markup)
    else:
        await event.answer(text=text, reply_markup=reply_markup)

@router.callback_query(F.data == "nav_profile")
async def handle_profile_request(callback: types.CallbackQuery):
    """Отображение личного кабинета пользователя."""
    profile_content = (
        "<b>👤 Личный кабинет</b>\n\n"
        "💳 <b>Ваш баланс:</b> 1,250 токенов\n"
        "⭐ <b>Статус:</b> Premium-подписка\n"
        "📅 <b>Действует до:</b> 15.10.2024\n\n"
        "<i>Используйте токены для генерации уникального контента.</i>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💎 Пополнить баланс", callback_data="nav_shop"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="nav_main"))
    
    await update_persistent_panel(callback, profile_content, builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "nav_main")
async def handle_main_menu_request(callback: types.CallbackQuery):
    """Возврат к основному интерфейсу выбора функций."""
    welcome_text = (
        "<b>Добро пожаловать в NeuroFox AI!</b>\n\n"
        "Выберите интересующий вас раздел генерации:"
    )
    await update_persistent_panel(
        callback, 
        welcome_text, 
        get_main_menu_keyboard()
    )
    await callback.answer()
