"""
Главный файл бота — точка входа
Визуальная новелла "Новые горизонты"
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, DATABASE_PATH
from database import Database
from game import GameEngine
from scenarios import load_all_scenarios
from handlers import commands_router, callbacks_router, game_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    db = Database(DATABASE_PATH)
    await db.init()
    
    # Загрузка сценариев
    logger.info("Загрузка сценариев...")
    load_all_scenarios()
    
    # Создание игрового движка
    engine = GameEngine(db)
    
    # Создание бота и диспетчера
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация роутеров
    dp.include_router(commands_router)
    dp.include_router(game_router)
    dp.include_router(callbacks_router)
    
    # Middleware для передачи зависимостей
    @dp.update.middleware()
    async def dependency_middleware(handler, event, data):
        data["db"] = db
        data["engine"] = engine
        return await handler(event, data)
    
    # Запуск
    logger.info("Бот запускается...")
    
    try:
        # Удаляем webhook если есть
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Запускаем polling
        logger.info("Бот успешно запущен! Нажмите Ctrl+C для остановки.")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise