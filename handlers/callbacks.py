"""
Обработчики callback-запросов
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database import Database
from game import GameEngine, CHARACTERS
from keyboards import (
    get_main_menu_keyboard,
    get_back_to_game_keyboard,
    get_character_keyboard,
    get_continue_keyboard,
)
from .commands import GameStates
from .game import send_scene

router = Router()


@router.callback_query(F.data == "start_game")
async def cb_start_game(callback: CallbackQuery, state: FSMContext, db: Database):
    """Начать новую игру"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Создаём игрока если нет
    player = await db.get_player(user_id)
    if not player:
        await db.create_player(user_id, callback.from_user.username)
    
    await state.set_state(GameStates.entering_name)
    
    await callback.message.edit_text(
        "✏️ *Как тебя зовут?*\n\n"
        "Введи имя своего персонажа (2-20 символов):\n\n"
        "_Это имя будут использовать другие персонажи_",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "continue_game")
async def cb_continue_game(callback: CallbackQuery, state: FSMContext, db: Database, engine: GameEngine):
    """Продолжить игру"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    scene, save = await engine.get_current_scene(user_id)
    
    if not scene or not save:
        await callback.message.edit_text(
            "❌ Нет сохранения! Начни новую игру.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    player = await db.get_player(user_id)
    player_name = player.player_name if player else "Герой"
    
    await state.set_state(GameStates.playing)
    await send_scene(callback, scene, save, player_name, engine)


@router.callback_query(F.data == "restart_game")
async def cb_restart_game(callback: CallbackQuery):
    """Показать подтверждение рестарта"""
    from keyboards import get_confirm_restart_keyboard
    
    await callback.answer()
    await callback.message.edit_text(
        "⚠️ *Ты уверен?*\n\n"
        "Это удалит всё твоё сохранение и начнёт игру заново.",
        parse_mode="Markdown",
        reply_markup=get_confirm_restart_keyboard()
    )


@router.callback_query(F.data == "confirm_restart")
async def cb_confirm_restart(callback: CallbackQuery, state: FSMContext, db: Database):
    """Подтверждение рестарта"""
    await callback.answer("🔄 Сохранение удалено!")
    
    user_id = callback.from_user.id
    await db.delete_save(user_id)
    
    await state.set_state(GameStates.entering_name)
    
    await callback.message.edit_text(
        "🆕 *Новое начало!*\n\n"
        "Введи имя своего персонажа:",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "cancel_restart")
async def cb_cancel_restart(callback: CallbackQuery):
    """Отмена рестарта"""
    await callback.answer("✅ Отменено")
    await callback.message.edit_text(
        "👌 *Продолжаем!*\n\n"
        "Выбери действие:",
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "show_characters")
async def cb_show_characters(callback: CallbackQuery):
    """Показать персонажей"""
    await callback.answer()
    
    text = """
👥 *ПЕРСОНАЖИ*

Выбери персонажа для подробной информации:
    """
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_character_keyboard()
    )


@router.callback_query(F.data.startswith("char_"))
async def cb_show_character(callback: CallbackQuery):
    """Показать конкретного персонажа"""
    char_id = callback.data.replace("char_", "")
    
    char = CHARACTERS.get(char_id)
    if not char:
        await callback.answer("❌ Персонаж не найден")
        return
    
    await callback.answer()
    await callback.message.edit_text(
        char.get_full_info(),
        parse_mode="Markdown",
        reply_markup=get_character_keyboard()
    )


@router.callback_query(F.data == "show_stats")
async def cb_show_stats(callback: CallbackQuery, db: Database, engine: GameEngine):
    """Показать статистику"""
    await callback.answer()
    
    user_id = callback.from_user.id
    save = await db.get_save(user_id)
    
    if not save:
        await callback.message.edit_text(
            "❌ Нет сохранения!",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    stats_text = engine.format_stats(save)
    stats_text += f"\n\n📍 *Текущая глава:* {save.chapter}"
    
       achievements = await db.get_achievements(user_id)
    if achievements:
        stats_text += f"\n🏆 *Достижения:* {len(achievements)}"
    
    await callback.message.edit_text(
        stats_text,
        parse_mode="Markdown",
        reply_markup=get_back_to_game_keyboard()
    )


@router.callback_query(F.data == "show_help")
async def cb_show_help(callback: CallbackQuery):
    """Показать справку"""
    await callback.answer()
    
    help_text = """
📖 *ПОМОЩЬ*

*Как играть:*
• Читай текст и выбирай варианты ответов
• Твои выборы влияют на сюжет и отношения
• У каждого персонажа — своя история
• Достигай разных концовок!

*Команды:*
/start — Главное меню
/continue — Продолжить игру
/restart — Начать заново
/stats — Отношения
/characters — Персонажи
/help — Справка

*Советы:*
💡 Нет "правильных" выборов
💡 Исследуй разные ветки!
💡 Игра сохраняется автоматически
    """
    await callback.message.edit_text(
        help_text,
        parse_mode="Markdown",
        reply_markup=get_back_to_game_keyboard()
    )


@router.callback_query(F.data == "back_to_game")
async def cb_back_to_game(callback: CallbackQuery, state: FSMContext, db: Database, engine: GameEngine):
    """Вернуться к игре"""
    await callback.answer()
    
    user_id = callback.from_user.id
    scene, save = await engine.get_current_scene(user_id)
    
    if scene and save:
        player = await db.get_player(user_id)
        player_name = player.player_name if player else "Герой"
        await state.set_state(GameStates.playing)
        await send_scene(callback, scene, save, player_name, engine)
    else:
        await callback.message.edit_text(
            "🎮 *Главное меню*\n\nВыбери действие:",
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard()
        )


@router.callback_query(F.data.startswith("choice_"))
async def cb_process_choice(callback: CallbackQuery, state: FSMContext, db: Database, engine: GameEngine):
    """Обработка выбора игрока"""
    choice_id = callback.data.replace("choice_", "")
    user_id = callback.from_user.id
    
    # Делаем выбор
    new_scene, save, achievement_unlocked, achievement_id = await engine.make_choice(user_id, choice_id)
    
    if not new_scene:
        await callback.answer("❌ Ошибка выбора!")
        return
    
    # Уведомление о достижении
    if achievement_unlocked:
        achievement_names = {
            "adventurer": "🏆 Искатель приключений",
            "presenter": "🏆 Оратор",
            "romantic": "🏆 Романтик",
            "friend": "🏆 Верный друг",
        }
        ach_name = achievement_names.get(achievement_id, f"🏆 {achievement_id}")
        await callback.answer(f"✨ Достижение разблокировано: {ach_name}!", show_alert=True)
    else:
        await callback.answer()
    
    # Получаем имя игрока
    player = await db.get_player(user_id)
    player_name = player.player_name if player else "Герой"
    
    # Показываем новую сцену
    await send_scene(callback, new_scene, save, player_name, engine)