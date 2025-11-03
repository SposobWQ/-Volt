import os
import sys
import asyncio
from dotenv import load_dotenv

# Добавляем пути для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'cogs'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from core.bot import PerfectMusicBot
from core.logger import logger

# Загрузка переменных окружения
load_dotenv()

async def main():
    logger.success("Запуск Discord Music Bot...", "🎵")
    logger.info("=" * 50)
    
    try:
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            logger.error("DISCORD_BOT_TOKEN не найден в .env файле")
            logger.info("Создайте файл .env с содержимым: DISCORD_BOT_TOKEN=your_token_here")
            return
        
        logger.info(f"Токен загружен: {token[:20]}...", "🔑")
        
        bot = PerfectMusicBot()
        
        logger.info("Запуск бота...", "🚀")
        await bot.start(token)
        
    except KeyboardInterrupt:
        logger.warning("Остановка бота по запросу пользователя...", "⏹️")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'bot' in locals():
            await bot.close()

def run_bot():
    """Функция для запуска бота (нужна для хостинга)"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.success("Бот завершил работу", "👋")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")

if __name__ == "__main__":
    run_bot()