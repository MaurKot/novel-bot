"""
Inline-клавиатуры бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List
from game.scenes import SceneChoice


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="▶️ Начать игру", callback_data="start_game")
    )
    builder.row(
        InlineKeyboardButton(text="📖 Продолжить", callback_data="continue_game"),
        InlineKeyboardButton(text="🔄 Заново", callback_data="restart_game")
    )
    builder.row(
        InlineKeyboardButton(text="👥 Персонажи", callback_data="show_characters"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="show_stats")
    )
    builder.row(
        InlineKeyboardButton(text="❓ Помощь", callback_data="show_help")
    )
    return builder.as_markup()


def get_scene_choices_keyboard(choices: List[SceneChoice]) -> InlineKeyboardMarkup:
    """Клавиатура для выборов в сцене"""
    builder = InlineKeyboardBuilder()
    
    for choice in choices:
        builder.row(
            InlineKeyboardButton(
                text=choice.text,
                callback_data=f"choice_{choice.id}"
            )
        )
    
    return builder.as_markup()


def get_continue_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для продолжения (для сцен без выборов)"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="▶️ Продолжить", callback_data="next_scene")
    )
    return builder.as_markup()


def get_confirm_restart_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения рестарта"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да, начать заново", callback_data="confirm_restart"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_restart")
    )
    return builder.as_markup()


def get_back_to_game_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата к игре"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎮 Вернуться к игре", callback_data="back_to_game")
    )
    return builder.as_markup()


def get_name_confirm_keyboard(name: str) -> InlineKeyboardMarkup:
    """Подтверждение имени"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"✅ Да, я — {name}", callback_data="confirm_name"),
        InlineKeyboardButton(text="✏️ Изменить имя", callback_data="change_name")
    )
    return builder.as_markup()


def get_character_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для просмотра персонажей"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎨 Алекс", callback_data="char_alex"),
        InlineKeyboardButton(text="🖋️ Дамиан", callback_data="char_damian")
    )
    builder.row(
        InlineKeyboardButton(text="📸 Марк", callback_data="char_mark"),
        InlineKeyboardButton(text="🏛️ Виктор", callback_data="char_victor")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_game")
    )
    return builder.as_markup()