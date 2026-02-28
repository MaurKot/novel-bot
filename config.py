"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Путь к базе данных
DATABASE_PATH = "game_data.db"

# Настройки игры
GAME_SETTINGS = {
    "max_affection": 100,
    "affection_per_choice": 5,
    "special_choice_bonus": 10,
}

# URL изображений-заглушек (можно заменить на реальные)
DEFAULT_IMAGES = {
    "city": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800",
    "coffee_shop": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800",
    "apartment": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800",
    "office": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800",
    "park": "https://images.unsplash.com/photo-1541417904950-b855846fe074?w=800",
    "night_city": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800",
    "rain": "https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=800",
    "sunset": "https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=800",
    "bookstore": "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=800",
    "gallery": "https://images.unsplash.com/photo-1577720643272-265f09367456?w=800",
}