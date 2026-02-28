"""
Система сцен
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable


@dataclass
class SceneChoice:
    """Вариант выбора в сцене"""
    id: str
    text: str
    next_scene: str
    
    # Изменение очков привязанности
    affection_changes: Dict[str, int] = field(default_factory=dict)
    
    # Флаги, которые устанавливает выбор
    sets_flags: Dict[str, bool] = field(default_factory=dict)
    
    # Условие отображения (требуемые флаги)
    requires_flags: Dict[str, bool] = field(default_factory=dict)
    
    # Минимальные очки привязанности для разблокировки
    requires_affection: Dict[str, int] = field(default_factory=dict)
    
    # Достижение, которое открывает выбор
    unlocks_achievement: Optional[str] = None
    
    # Является ли выбор "особенным" (больше очков)
    is_special: bool = False


@dataclass
class Scene:
    """Сцена игры"""
    id: str
    chapter: int
    title: str
    text: str
    image_url: Optional[str] = None
    
    # Варианты выбора
    choices: List[SceneChoice] = field(default_factory=list)
    
    # Автопереход на следующую сцену (если нет выборов)
    next_scene: Optional[str] = None
    
    # Персонаж, который говорит в этой сцене
    speaking_character: Optional[str] = None
    
    # Флаги, устанавливаемые при входе в сцену
    sets_flags: Dict[str, bool] = field(default_factory=dict)
    
    # Условие для отображения сцены
    requires_flags: Dict[str, bool] = field(default_factory=dict)
    
    # Это концовка?
    is_ending: bool = False
    ending_type: Optional[str] = None  # "good", "neutral", "bad", "secret"
    
    # Музыка/атмосфера (для описания)
    mood: Optional[str] = None
    
    def get_available_choices(
        self, 
        story_flags: Dict[str, bool], 
        affection: Dict[str, int]
    ) -> List[SceneChoice]:
        """Получить доступные варианты выбора"""
        available = []
        for choice in self.choices:
            # Проверяем флаги
            flags_ok = all(
                story_flags.get(flag) == value
                for flag, value in choice.requires_flags.items()
            )
            # Проверяем привязанность
            affection_ok = all(
                affection.get(char, 0) >= value
                for char, value in choice.requires_affection.items()
            )
            if flags_ok and affection_ok:
                available.append(choice)
        return available
    
    def format_text(self, player_name: str = "Герой") -> str:
        """Форматировать текст сцены, подставляя имя игрока"""
        return self.text.replace("{player}", player_name)


# Хранилище всех сцен
ALL_SCENES: Dict[str, Scene] = {}


def register_scene(scene: Scene):
    """Зарегистрировать сцену в системе"""
    ALL_SCENES[scene.id] = scene


def get_scene(scene_id: str) -> Optional[Scene]:
    """Получить сцену по ID"""
    return ALL_SCENES.get(scene_id)


def get_scenes_by_chapter(chapter: int) -> List[Scene]:
    """Получить все сцены главы"""
    return [s for s in ALL_SCENES.values() if s.chapter == chapter]