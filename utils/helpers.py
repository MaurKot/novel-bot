"""
Вспомогательные функции
"""
import re
from typing import Optional


def format_progress_bar(value: int, max_value: int = 100, length: int = 10) -> str:
    """
    Создать прогресс-бар из эмодзи
    
    Args:
        value: Текущее значение
        max_value: Максимальное значение
        length: Длина прогресс-бара
    
    Returns:
        Строка прогресс-бара
    """
    filled = int(value / max_value * length)
    empty = length - filled
    bar = "▰" * filled + "▱" * empty
    return f"{bar} {value}%"


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Обрезать текст до максимальной длины
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
        suffix: Суффикс для обрезанного текста
    
    Returns:
        Обрезанный текст
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def escape_markdown(text: str) -> str:
    """
    Экранировать специальные символы Markdown
    
    Args:
        text: Исходный текст
    
    Returns:
        Экранированный текст
    """
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def get_relationship_level(affection: int) -> tuple[str, str]:
    """
    Получить уровень отношений и эмодзи
    
    Args:
        affection: Очки привязанности
    
    Returns:
        Кортеж (название уровня, эмодзи)
    """
    if affection >= 81:
        return "Особая связь", "💕"
    elif affection >= 61:
        return "Близкие друзья", "💜"
    elif affection >= 41:
        return "Приятели", "💙"
    elif affection >= 21:
        return "Знакомые", "🤝"
    else:
        return "Незнакомцы", "👤"


def format_choice_text(text: str, is_special: bool = False) -> str:
    """
    Форматировать текст выбора
    
    Args:
        text: Текст выбора
        is_special: Является ли выбор особенным
    
    Returns:
        Отформатированный текст
    """
    if is_special:
        return f"⭐ {text}"
    return text


def calculate_ending(
    alex: int, 
    damian: int, 
    mark: int, 
    victor: int,
    flags: dict
) -> str:
    """
    Определить концовку на основе отношений и флагов
    
    Args:
        alex: Очки с Алексом
        damian: Очки с Дамианом
        mark: Очки с Марком
        victor: Очки с Виктором
        flags: Флаги истории
    
    Returns:
        ID концовки
    """
    # Секретная концовка — если высокие отношения со всеми
    if all(x >= 70 for x in [alex, damian, mark, victor]):
        return "ending_secret"
    
    # Находим максимум
    scores = {
        "alex": alex,
        "damian": damian,
        "mark": mark,
        "victor": victor
    }
    
    max_char = max(scores, key=scores.get)
    max_score = scores[max_char]
    
    # Хорошая концовка — если >= 80
    if max_score >= 80:
        return f"ending_{max_char}_good"
    
    # Нейтральная концовка
    return "ending_neutral"


def format_achievement_notification(achievement_id: str) -> str:
    """
    Форматировать уведомление о достижении
    
    Args:
        achievement_id: ID достижения
    
    Returns:
        Отформатированный текст
    """
    achievements = {
        "adventurer": ("🏔️ Искатель приключений", "Согласился на рискованное предложение"),
        "presenter": ("🎤 Мастер презентаций", "Успешно провёл презентацию"),
        "romantic": ("💕 Романтик", "Первый романтический момент"),
        "friend": ("🤝 Верный друг", "Поддержал друга в трудную минуту"),
        "artist": ("🎨 Ценитель искусства", "Глубоко понял работы Алекса"),
        "writer": ("📚 Книжный червь", "Прочитал книгу Дамиана"),
        "photographer": ("📸 Фотомодель", "Согласился на фотосессию"),
        "architect": ("🏛️ Архитектор душ", "Понял глубину Виктора"),
        "explorer": ("🌃 Исследователь ночи", "Посетил все секретные места"),
        "heartthrob": ("💘 Покоритель сердец", "Достиг высоких отношений со всеми"),
    }
    
    if achievement_id in achievements:
        name, description = achievements[achievement_id]
        return f"✨ *ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!*\n\n{name}\n_{description}_"
    
    return f"✨ Достижение: {achievement_id}"


def get_mood_emoji(mood: Optional[str]) -> str:
    """
    Получить эмодзи настроения сцены
    
    Args:
        mood: Настроение сцены
    
    Returns:
        Эмодзи
    """
    moods = {
        "happy": "😊",
        "sad": "😢",
        "romantic": "💕",
        "tense": "😰",
        "mysterious": "🌙",
        "exciting": "⚡",
        "calm": "🌸",
        "dramatic": "🎭",
    }
    return moods.get(mood, "")