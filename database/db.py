"""
Работа с базой данных SQLite
"""
import aiosqlite
import json
from datetime import datetime
from typing import Optional
from .models import PlayerData, GameSave


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    async def init(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица игроков
            await db.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    player_name TEXT DEFAULT 'Герой',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица сохранений
            await db.execute("""
                CREATE TABLE IF NOT EXISTS game_saves (
                    user_id INTEGER PRIMARY KEY,
                    current_scene TEXT DEFAULT 'prologue_1',
                    chapter INTEGER DEFAULT 0,
                    affection_alex INTEGER DEFAULT 0,
                    affection_damian INTEGER DEFAULT 0,
                    affection_mark INTEGER DEFAULT 0,
                    affection_victor INTEGER DEFAULT 0,
                    story_flags TEXT DEFAULT '{}',
                    choices_history TEXT DEFAULT '[]',
                    achievements TEXT DEFAULT '[]',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            """)
            
            # Таблица достижений
            await db.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    achievement_id TEXT,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            """)
            
            await db.commit()
    
    async def get_player(self, user_id: int) -> Optional[PlayerData]:
        """Получить данные игрока"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM players WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return PlayerData(
                        user_id=row["user_id"],
                        username=row["username"],
                        player_name=row["player_name"],
                    )
                return None
    
    async def create_player(self, user_id: int, username: str = None) -> PlayerData:
        """Создать нового игрока"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO players (user_id, username) VALUES (?, ?)",
                (user_id, username)
            )
            await db.commit()
        return PlayerData(user_id=user_id, username=username)
    
    async def update_player_name(self, user_id: int, name: str):
        """Обновить имя игрока"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE players SET player_name = ? WHERE user_id = ?",
                (name, user_id)
            )
            await db.commit()
    
    async def get_save(self, user_id: int) -> Optional[GameSave]:
        """Получить сохранение игры"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM game_saves WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return GameSave(
                        user_id=row["user_id"],
                        current_scene=row["current_scene"],
                        chapter=row["chapter"],
                        affection_alex=row["affection_alex"],
                        affection_damian=row["affection_damian"],
                        affection_mark=row["affection_mark"],
                        affection_victor=row["affection_victor"],
                        story_flags=row["story_flags"],
                        choices_history=row["choices_history"],
                        achievements=row["achievements"],
                    )
                return None
    
    async def create_save(self, user_id: int) -> GameSave:
        """Создать новое сохранение"""
        save = GameSave(user_id=user_id)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO game_saves 
                (user_id, current_scene, chapter, affection_alex, affection_damian,
                 affection_mark, affection_victor, story_flags, choices_history, achievements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, save.current_scene, save.chapter,
                save.affection_alex, save.affection_damian,
                save.affection_mark, save.affection_victor,
                save.story_flags, save.choices_history, save.achievements
            ))
            await db.commit()
        return save
    
    async def update_save(self, save: GameSave):
        """Обновить сохранение"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE game_saves SET
                    current_scene = ?,
                    chapter = ?,
                    affection_alex = ?,
                    affection_damian = ?,
                    affection_mark = ?,
                    affection_victor = ?,
                    story_flags = ?,
                    choices_history = ?,
                    achievements = ?,
                    updated_at = ?
                WHERE user_id = ?
            """, (
                save.current_scene, save.chapter,
                save.affection_alex, save.affection_damian,
                save.affection_mark, save.affection_victor,
                save.story_flags, save.choices_history, save.achievements,
                datetime.now(), save.user_id
            ))
            await db.commit()
    
    async def delete_save(self, user_id: int):
        """Удалить сохранение"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM game_saves WHERE user_id = ?", (user_id,)
            )
            await db.commit()
    
    async def add_achievement(self, user_id: int, achievement_id: str):
        """Добавить достижение"""
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем, нет ли уже такого достижения
            async with db.execute(
                "SELECT id FROM achievements WHERE user_id = ? AND achievement_id = ?",
                (user_id, achievement_id)
            ) as cursor:
                if await cursor.fetchone():
                    return False  # Уже есть
            
            await db.execute(
                "INSERT INTO achievements (user_id, achievement_id) VALUES (?, ?)",
                (user_id, achievement_id)
            )
            await db.commit()
            return True
    
    async def get_achievements(self, user_id: int) -> list:
        """Получить список достижений"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT achievement_id FROM achievements WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]