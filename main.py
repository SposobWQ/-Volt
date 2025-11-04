import os
import sys
import asyncio
from dotenv import load_dotenv
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Добавляем пути для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'cogs'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from core.bot import PerfectMusicBot
from core.logger import logger

# Загрузка переменных окружения
load_dotenv()

# Проверка и настройка аудио для Replit
def setup_audio():
    """Настройка аудио для работы в Replit"""
    try:
        import discord
        
        # Проверяем загружен ли opus
        if not discord.opus.is_loaded():
            try:
                # Пробуем разные пути к opus
                opus_paths = [
                    '/usr/lib/x86_64-linux-gnu/libopus.so.0',
                    '/usr/lib/libopus.so.0',
                    'libopus.so.0',
                    'opus'
                ]
                
                for path in opus_paths:
                    try:
                        discord.opus.load_opus(path)
                        if discord.opus.is_loaded():
                            logger.success(f"Opus загружен: {path}", "🔊")
                            break
                    except:
                        continue
                
                if not discord.opus.is_loaded():
                    logger.warning("Opus не загружен, возможны проблемы с аудио", "⚠️")
            except Exception as e:
                logger.warning(f"Не удалось загрузить opus: {e}", "⚠️")
        
        # Проверяем наличие ffmpeg
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.success("FFmpeg доступен", "🎵")
            else:
                logger.warning("FFmpeg не доступен", "⚠️")
        except:
            logger.warning("FFmpeg не установлен", "⚠️")
            
    except ImportError as e:
        logger.error(f"Ошибка импорта: {e}", "❌")

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Bot is running!')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Отключаем логи HTTP запросов
        return

def start_http_server():
    """Запускает HTTP сервер в отдельном потоке"""
    def run_server():
        port = int(os.environ.get('PORT', 10000))
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.success(f"HTTP сервер запущен на порту {port}", "🌐")
        server.serve_forever()
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

async def main():
    logger.success("Запуск Discord Music Bot...", "🎵")
    logger.info("=" * 50)
    
    # Настраиваем аудио
    setup_audio()
    
    # Запускаем HTTP сервер
    start_http_server()
    
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