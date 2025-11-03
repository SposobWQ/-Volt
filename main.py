import os
import sys
import asyncio
from dotenv import load_dotenv
import threading

# Добавляем пути для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'cogs'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from core.bot import PerfectMusicBot
from core.logger import logger

# Загрузка переменных окружения
load_dotenv()

def start_simple_server():
    """Запускает простой TCP сервер в отдельном потоке"""
    import socket
    import time
    
    def server_thread():
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('0.0.0.0', 10000))
                sock.listen(1)
                logger.success("TCP сервер запущен на порту 10000", "🌐")
                
                while True:
                    conn, addr = sock.accept()
                    conn.send(b"Bot is running!")
                    conn.close()
                    
            except Exception as e:
                logger.warning(f"Ошибка TCP сервера: {e}")
                time.sleep(5)
    
    thread = threading.Thread(target=server_thread, daemon=True)
    thread.start()

async def main():
    logger.success("Запуск Discord Music Bot...", "🎵")
    logger.info("=" * 50)
    
    # Запускаем TCP сервер
    start_simple_server()
    
    try:
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            logger.error("DISCORD_BOT_TOKEN не найден в .env файле")
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

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.success("Бот завершил работу", "👋")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")