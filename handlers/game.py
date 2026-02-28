"""
Игровая логика и отправка сцен
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import Database, GameSave
from game import GameEngine, Scene, CHARACTERS
from keyboards import get_scene_choices_keyboard, get_continue_keyboard
from .commands import GameStates

router = Router()


async def send_scene(
    target: Message | CallbackQuery,
    scene: Scene,
    save: GameSave,
    player_name: str,
    engine: GameEngine
):
    """Отправить сцену игроку"""
    # Форматируем текст
    text = scene.format_text(player_name)
    
    # Добавляем заголовок главы если нужно
    if scene.chapter > 0 and "ГЛАВА" not in text[:50]:
        chapter_names = {
            0: "Пролог",
            1: "Глава 1: Первый день",
            2: "Глава 2: Сближение", 
            3: "Глава 3: Испытания",
            99: "Эпилог"
        }
        chapter_name = chapter_names.get(scene.chapter, f"Глава {scene.chapter}")
        text = f"📖 _{chapter_name}_\n\n{text}"
    
    # Добавляем информацию о говорящем персонаже
    if scene.speaking_character:
        char = CHARACTERS.get(scene.speaking_character)
        if char:
            text = f"{char.emoji} **{char.name}**\n\n{text}"
    
    # Получаем доступные выборы
    choices = await engine.get_available_choices_for_scene(scene, save)
    
    # Определяем клавиатуру
    if choices:
        keyboard = get_scene_choices_keyboard(choices)
    elif scene.next_scene:
        keyboard = get_continue_keyboard()
    else:
        keyboard = None
    
    # Если это концовка
    if scene.is_ending:
        text += "\n\n🎭 *КОНЕЦ*"
        keyboard = None
    
    # Отправляем или редактируем сообщение
    send_kwargs = {
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": keyboard
    }
    
    # Если есть изображение
    if scene.image_url:
        try:
            if isinstance(target, CallbackQuery):
                # Удаляем старое сообщение и отправляем новое с фото
                await target.message.delete()
                await target.message.answer_photo(
                    photo=scene.image_url,
                    caption=text[:1024],  # Ограничение на caption
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
                # Если текст длинный — отправляем остаток
                if len(text) > 1024:
                    await target.message.answer(
                        text[1024:],
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
            else:
                await target.answer_photo(
                    photo=scene.image_url,
                    caption=text[:1024],
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
        except Exception:
            # Если фото не загрузилось — просто текст
            if isinstance(target, CallbackQuery):
                await target.message.edit_text(**send_kwargs)
            else:
                await target.answer(**send_kwargs)
    else:
        if isinstance(target, CallbackQuery):
            try:
                await target.message.edit_text(**send_kwargs)
            except Exception:
                await target.message.answer(**send_kwargs)
        else:
            await target.answer(**send_kwargs)


@router.message(GameStates.entering_name)
async def process_name(message: Message, state: FSMContext, db: Database, engine: GameEngine):
    """Обработка ввода имени"""
    name = message.text.strip()
    
    # Валидация имени
    if len(name) < 2 or len(name) > 20:
        await message.answer(
            "❌ Имя должно быть от 2 до 20 символов. Попробуй ещё раз:"
        )
        return
    
    if not name.replace(" ", "").isalpha():
        await message.answer(
            "❌ Имя должно содержать только буквы. Попробуй ещё раз:"
        )
        return
    
    user_id = message.from_user.id
    
    # Сохраняем имя
    await db.update_player_name(user_id, name)
    
    # Создаём новое сохранение
    save = await engine.start_new_game(user_id, message.from_user.username)
    await db.update_player_name(user_id, name)
    
    # Переходим в режим игры
    await state.set_state(GameStates.playing)
    
    # Приветствие
    await message.answer(
        f"✨ *Прекрасно, {name}!*\n\n"
        "Твоя история начинается...\n\n"
        "_Нажми кнопку, чтобы продолжить_",
        parse_mode="Markdown",
        reply_markup=get_continue_keyboard()
    )


@router.callback_query(F.data == "next_scene")
async def process_next_scene(callback: CallbackQuery, state: FSMContext, db: Database, engine: GameEngine):
    """Переход к следующей сцене (для сцен без выборов)"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    scene, save = await engine.get_current_scene(user_id)
    
    if not scene or not save:
        await callback.message.edit_text(
            "❌ Ошибка! Используй /start чтобы начать заново."
        )
        return
    
    # Если есть next_scene — переходим
    if scene.next_scene:
        new_scene, save = await engine.go_to_scene(user_id, scene.next_scene)
        if new_scene:
            player = await db.get_player(user_id)
            player_name = player.player_name if player else "Герой"
            await send_scene(callback, new_scene, save, player_name, engine)
        else:
            await callback.message.edit_text("❌ Сцена не найдена!")
    else:
        await callback.message.edit_text(
            "🎭 *Конец этой ветки!*\n\nИспользуй /stats для просмотра прогресса.",
            parse_mode="Markdown"
        )