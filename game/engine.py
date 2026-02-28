"""
Игровой движок — обрабатывает логику игры
"""
import json
from typing import Optional, Tuple, List
from database import Database, GameSave
from .scenes import Scene, SceneChoice, get_scene
from .characters import CHARACTERS


class GameEngine:
    """Основной класс игрового движка"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def start_new_game(self, user_id: int, username: str = None) -> GameSave:
        """Начать новую игру"""
        # Создаём/обновляем игрока
        await self.db.create_player(user_id, username)
        # Удаляем старое сохранение если есть
        await self.db.delete_save(user_id)
        # Создаём новое сохранение
        save = await self.db.create_save(user_id)
        return save
    
    async def get_current_scene(self, user_id: int) -> Tuple[Optional[Scene], Optional[GameSave]]:
        """Получить текущую сцену игрока"""
        save = await self.db.get_save(user_id)
        if not save:
            return None, None
        
        scene = get_scene(save.current_scene)
        return scene, save
    
    async def make_choice(
        self, 
        user_id: int, 
        choice_id: str
    ) -> Tuple[Optional[Scene], Optional[GameSave], bool, Optional[str]]:
        """
        Обработать выбор игрока
        Возвращает: (новая_сцена, сохранение, открыто_достижение, id_достижения)
        """
        save = await self.db.get_save(user_id)
        if not save:
            return None, None, False, None
        
        current_scene = get_scene(save.current_scene)
        if not current_scene:
            return None, save, False, None
        
        # Находим выбранный вариант
        choice = None
        for c in current_scene.choices:
            if c.id == choice_id:
                choice = c
                break
        
        if not choice:
            return current_scene, save, False, None
        
        # Применяем изменения привязанности
        for char, delta in choice.affection_changes.items():
            current = getattr(save, f"affection_{char}", 0)
            setattr(save, f"affection_{char}", max(0, min(100, current + delta)))
        
        # Устанавливаем флаги
        story_flags = json.loads(save.story_flags)
        for flag, value in choice.sets_flags.items():
            story_flags[flag] = value
        save.story_flags = json.dumps(story_flags)
        
        # Добавляем выбор в историю
        choices_history = json.loads(save.choices_history)
        choices_history.append({
            "scene": save.current_scene,
            "choice": choice_id,
        })
        save.choices_history = json.dumps(choices_history)
        
        # Переходим к следующей сцене
        save.current_scene = choice.next_scene
        
        # Получаем новую сцену
        new_scene = get_scene(choice.next_scene)
        if new_scene:
            save.chapter = new_scene.chapter
            
            # Устанавливаем флаги сцены
            for flag, value in new_scene.sets_flags.items():
                story_flags[flag] = value
            save.story_flags = json.dumps(story_flags)
        
        # Проверяем достижение
        achievement_unlocked = False
        achievement_id = None
        if choice.unlocks_achievement:
            achievement_unlocked = await self.db.add_achievement(
                user_id, choice.unlocks_achievement
            )
            if achievement_unlocked:
                achievement_id = choice.unlocks_achievement
        
        # Сохраняем
        await self.db.update_save(save)
        
        return new_scene, save, achievement_unlocked, achievement_id
    
    async def go_to_scene(self, user_id: int, scene_id: str) -> Tuple[Optional[Scene], Optional[GameSave]]:
        """Перейти к конкретной сцене (для авто-переходов)"""
        save = await self.db.get_save(user_id)
        if not save:
            return None, None
        
        scene = get_scene(scene_id)
        if scene:
            save.current_scene = scene_id
            save.chapter = scene.chapter
            
            # Устанавливаем флаги сцены
            if scene.sets_flags:
                story_flags = json.loads(save.story_flags)
                for flag, value in scene.sets_flags.items():
                    story_flags[flag] = value
                save.story_flags = json.dumps(story_flags)
            
            await self.db.update_save(save)
        
        return scene, save
    
    def get_affection_dict(self, save: GameSave) -> dict:
        """Получить словарь привязанностей"""
        return {
            "alex": save.affection_alex,
            "damian": save.affection_damian,
            "mark": save.affection_mark,
            "victor": save.affection_victor,
        }
    
    def get_story_flags(self, save: GameSave) -> dict:
        """Получить флаги истории"""
        return json.loads(save.story_flags)
    
    def format_stats(self, save: GameSave) -> str:
        """Форматировать статистику отношений"""
        def progress_bar(value: int, max_value: int = 100) -> str:
            filled = int(value / max_value * 10)
            empty = 10 - filled
            bar = "▰" * filled + "▱" * empty
            return f"{bar} {value}%"
        
        result = "📊 *ОТНОШЕНИЯ*\n\n"
        
        for char_id, char in CHARACTERS.items():
            affection = save.get_affection(char_id)
            result += f"{char.emoji} *{char.name}*\n"
            result += f"└ {progress_bar(affection)}\n\n"
        
        # Добавляем уровни отношений
        result += "\n📈 *Уровни:*\n"
        result += "• 0-20: Незнакомцы\n"
        result += "• 21-40: Знакомые\n"
        result += "• 41-60: Приятели\n"
        result += "• 61-80: Близкие друзья\n"
        result += "• 81-100: Особая связь 💕\n"
        
        return result
    
    async def get_available_choices_for_scene(
        self, 
        scene: Scene, 
        save: GameSave
    ) -> List[SceneChoice]:
        """Получить доступные выборы для сцены"""
        story_flags = self.get_story_flags(save)
        affection = self.get_affection_dict(save)
        return scene.get_available_choices(story_flags, affection)