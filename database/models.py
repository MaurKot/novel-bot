"""
Модели данных для игры
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class PlayerData:
    """Данные игрока"""
    user_id: int
    username: Optional[str] = None
    player_name: str = "Герой"
    created_at: datetime = field(default_factory=datetime.now)
    
    
@dataclass
class GameSave:
    """Сохранение игры"""
    user_id: int
    current_scene: str = "prologue_1"
    chapter: int = 0
    
    # Очки привязанности к персонажам
    affection_alex: int = 0
    affection_damian: int = 0
    affection_mark: int = 0
    affection_victor: int = 0
    
    # Флаги сюжета (JSON-строка)
    story_flags: str = "{}"
    
    # История выборов (JSON-строка)
    choices_history: str = "[]"
    
    # Достижения (JSON-строка)
    achievements: str = "[]"
    
    # Время
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_affection(self, character: str) -> int:
        """Получить очки привязанности к персонажу"""
        affection_map = {
            "alex": self.affection_alex,
            "damian": self.affection_damian,
            "mark": self.affection_mark,
            "victor": self.affection_victor,
        }
        return affection_map.get(character.lower(), 0)
    
    def to_dict(self) -> dict:
        """Преобразовать в словарь"""
        return {
            "user_id": self.user_id,
            "current_scene": self.current_scene,
            "chapter": self.chapter,
            "affection_alex": self.affection_alex,
            "affection_damian": self.affection_damian,
            "affection_mark": self.affection_mark,
            "affection_victor": self.affection_victor,
            "story_flags": self.story_flags,
            "choices_history": self.choices_history,
            "achievements": self.achievements,
        }