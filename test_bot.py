import os
import sys
import asyncio
from dotenv import load_dotenv

def test_environment():
    """Тестируем окружение"""
    print("🔍 Тестирование окружения...")
    
    # Проверяем Python
    print(f"🐍 Python: {sys.version}")
    
    # Проверяем рабочую директорию
    print(f"📁 Рабочая директория: {os.getcwd()}")
    
    # Проверяем файлы
    files_to_check = ['.env', 'main.py', 'core/bot.py', 'cogs/music.py']
    for file in files_to_check:
        exists = os.path.exists(file)
        print(f"{'✅' if exists else '❌'} {file}: {'Найден' if exists else 'НЕ НАЙДЕН'}")
    
    # Проверяем .env
    load_dotenv()
    token = os.getenv('DISCORD_BOT_TOKEN')
    print(f"🔑 Токен: {'Найден' if token else 'НЕ НАЙДЕН'}")
    if token:
        print(f"🔑 Длина токена: {len(token)} символов")
        print(f"🔑 Начинается с: {token[:10]}...")

def test_imports():
    """Тестируем импорты"""
    print("\n📦 Тестирование импортов...")
    
    try:
        # Добавляем пути
        sys.path.append('core')
        sys.path.append('cogs') 
        sys.path.append('utils')
        
        import discord
        print(f"✅ discord.py: {discord.__version__}")
        
        import yt_dlp as youtube_dl
        print("✅ yt-dlp")
        
        from core.config import Config
        print("✅ core.config")
        
        from core.database import Database
        print("✅ core.database")
        
        from utils.music_classes import AdvancedMusicPlayer
        print("✅ utils.music_classes")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_bot():
    """Тестируем создание бота"""
    print("\n🤖 Тестирование создания бота...")
    
    try:
        from core.bot import PerfectMusicBot
        
        bot = PerfectMusicBot()
        print("✅ Бот создан успешно")
        
        # Тестируем setup_hook
        await bot.setup_hook()
        print("✅ Setup hook выполнен")
        
        return bot
        
    except Exception as e:
        print(f"❌ Ошибка создания бота: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("🎵 ТЕСТИРОВАНИЕ DISCORD BOT")
    print("=" * 50)
    
    # Тестируем окружение
    test_environment()
    
    # Тестируем импорты
    if not test_imports():
        print("\n❌ Критические ошибки импорта!")
        return
    
    # Тестируем бота
    bot = await test_bot()
    if not bot:
        print("\n❌ Ошибка создания бота!")
        return
    
    print("\n✅ Все тесты пройдены! Бот готов к запуску.")
    print("\n🚀 Запуск основного бота...")
    print("=" * 50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n🎯 Нажмите Enter для выхода...")