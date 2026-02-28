"""
Обработчики команд бота
"""
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from game import GameEngine, CHARACTERS
from keyboards import get_main_menu_keyboard, get_back_to_game_keyboard

router = Router()


class GameStates(StatesGroup):
    """Состояния игры"""
    entering_name = State()
    playing = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Database):
    """Команда /start"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Проверяем, есть ли сохранение
    save = await db.get_save(user_id)
    
    welcome_text = """
🌆 *НОВЫЕ ГОРИЗОНТЫ*
_Интерактивная визуальная новелла_

━━━━━━━━━━━━━━━━━━━━━━

Добро пожаловать в город, полный возможностей, встреч и... чувств.

Ты — тот, кто решил начать всё с чистого листа. Новый город, новая работа, новая жизнь.

И, возможно, новая любовь? 💕

━━━━━━━━━━━━━━━━━━━━━━

*Жанр:* Романтика (M/M)
*Рейтинг:* 16+
*Выборы имеют значение!*

━━━━━━━━━━━━━━━━━━━━━━
    """
    
    if save:
        welcome_text += f"\n📂 *У тебя есть сохранение!*\nГлава: {save.chapter} | Сцена: {save.current_scene}"
    
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда /help"""
    help_text = """
📖 *ПОМОЩЬ*

*Команды:*
/start — Главное меню
/continue — Продолжить игру
/restart — Начать заново
/stats — Отношения с персонажами
/characters — Информация о персонажах
/save — Сохранить игру (авто)
/help — Эта справка

*Как играть:*
• Читай текст и выбирай варианты ответов
• Твои выборы влияют на сюжет и отношения
• У каждого персонажа — своя история
• Достигай разных концовок!

*Советы:*
💡 Нет "правильных" выборов — только твои
💡 Следи за статистикой отношений
💡 Исследуй разные ветки!

Приятной игры! 🌟
    """
    await message.answer(help_text, parse_mode="Markdown", reply_markup=get_back_to_game_keyboard())


@router.message(Command("stats"))
async def cmd_stats(message: Message, db: Database, engine: GameEngine):
    """Команда /stats"""
    user_id = message.from_user.id
    save = await db.get_save(user_id)
    
    if not save:
        await message.answer(
            "❌ У тебя ещё нет сохранения! Начни игру командой /start",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    stats_text = engine.format_stats(save)
    
    # Добавляем информацию о прогрессе
    stats_text += f"\n\n📍 *Текущая глава:* {save.chapter}"
    
    # Достижения
    achievements = await db.get_achievements(user_id)
    if achievements:
        stats_text += f"\n🏆 *Достижения:* {len(achievements)}"
    
    await message.answer(stats_text, parse_mode="Markdown", reply_markup=get_back_to_game_keyboard())


@router.message(Command("characters"))
async def cmd_characters(message: Message):
    """Команда /characters"""
    from keyboards.inline import get_character_keyboard
    
    text = """
👥 *ПЕРСОНАЖИ*

Выбери персонажа, чтобы узнать больше:

🎨 *Алекс* — Бариста и художник
🖋️ *Дамиан* — Загадочный писатель  
📸 *Марк* — Энергичный фотограф
🏛️ *Виктор* — Серьёзный архитектор

Каждый из них уникален. Кто станет твоей судьбой?
    """
    await message.answer(text, parse_mode="Markdown", reply_markup=get_character_keyboard())


@router.message(Command("continue"))
async def cmd_continue(message: Message, state: FSMContext, db: Database, engine: GameEngine):
    """Команда /continue"""
    user_id = message.from_user.id
    
    scene, save = await engine.get_current_scene(user_id)
    
    if not scene or not save:
        await message.answer(
            "❌ Нет сохранения! Начни новую игру.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Получаем имя игрока
    player = await db.get_player(user_id)
    player_name = player.player_name if player else "Герой"
    
    # Отправляем текущую сцену
    await state.set_state(GameStates.playing)
    
    from handlers.game import send_scene
    await send_scene(message, scene, save, player_name, engine)


@router.message(Command("restart"))
async def cmd_restart(message: Message):
    """Команда /restart"""
    from keyboards import get_confirm_restart_keyboard
    
    await message.answer(
        "⚠️ *Ты уверен?*\n\nЭто удалит всё твоё сохранение и начнёт игру заново.",
        parse_mode="Markdown",
        reply_markup=get_confirm_restart_keyboard()
    )


@router.message(Command("save"))
async def cmd_save(message: Message, db: Database):
    """Команда /save"""
    save = await db.get_save(message.from_user.id)
    
    if save:
        await message.answer(
            "💾 *Игра автоматически сохраняется!*\n\n"
            f"📍 Глава: {save.chapter}\n"
            f"🎬 Сцена: {save.current_scene}\n\n"
            "Твой прогресс в безопасности 🌟",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "❌ Нет сохранения — сначала начни игру!",
            reply_markup=get_main_menu_keyboard()
        )