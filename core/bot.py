import discord
from discord.ext import commands
import yt_dlp as youtube_dlp
import os
import sys
import asyncio

# Добавляем путь для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Импортируем после добавления пути
from core.config import Config
from core.database import Database
from core.permissions import PermissionSystem
from core.logger import logger

class PerfectMusicBot(commands.Bot):
    def __init__(self):
        # Безопасные intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix=Config.DEFAULT_PREFIX,
            intents=intents,
            help_command=None
        )
        
        self.start_time = None
        self.db = Database()
        self.permissions = PermissionSystem(self.db)
        self.players = {}
        
        # Безопасные настройки yt-dlp
        self.ytdl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': True,
            'default_search': 'ytsearch:',
            'extractaudio': True,
            'audioformat': 'mp3',
        }
        self.ytdl = youtube_dlp.YoutubeDL(self.ytdl_opts)
        self.vote_skips = {}
        
    async def setup_hook(self):
        """Вызывается при инициализации бота"""
        self.start_time = asyncio.get_event_loop().time()
        logger.info("Инициализация бота...", "🔧")
        
        # Загрузка всех когов с обработкой ошибок
        cogs_to_load = [
            'cogs.music',
            'cogs.events',
            'cogs.admin',
            'cogs.voice_manager',  # ← ЗАПЯТАЯ ДОБАВЛЕНА
            'cogs.sync',
            'cogs.playlists'
        ]
        
        loaded_cogs = 0
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.success(f"Модуль {cog} загружен")
                loaded_cogs += 1
            except Exception as e:
                logger.error(f"Модуль {cog} не загружен: {e}")
        
        logger.info(f"Загружено модулей: {loaded_cogs}/{len(cogs_to_load)}")
        
        # Принудительная синхронизация команд
        try:
            logger.info("Синхронизация команд с Discord...", "🔄")
            synced = await self.tree.sync()
            logger.success(f"Синхронизировано {len(synced)} команд")
            for cmd in synced:
                logger.info(f"Команда: /{cmd.name}", "📋")
        except Exception as e:
            logger.error(f"Ошибка синхронизации команд: {e}")

    async def on_ready(self):
        """Вызывается когда бот готов к работе"""
        uptime = asyncio.get_event_loop().time() - self.start_time
        
        logger.success("=" * 50)
        logger.success("БОТ УСПЕШНО ЗАПУЩЕН!", "🎉")
        logger.success(f"Имя: {self.user.name}", "🤖")
        logger.success(f"ID: {self.user.id}", "🆔")
        logger.success(f"Серверов: {len(self.guilds)}", "📊")
        logger.success(f"Время запуска: {uptime:.2f} сек", "⏱️")
        logger.success("=" * 50)
        
        # Устанавливаем статус
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="/play для музыки"
        )
        await self.change_presence(activity=activity)

    async def close(self):
        """Корректное закрытие бота"""
        logger.info("Завершение работы бота...", "🔴")
        
        # Отключаемся от всех голосовых каналов
        disconnected = 0
        for guild_id, player in self.players.items():
            guild = self.get_guild(guild_id)
            if guild and guild.voice_client:
                await guild.voice_client.disconnect()
                disconnected += 1
                logger.voice(f"Отключен от сервера: {guild.name}")
        
        if disconnected > 0:
            logger.info(f"Отключено от {disconnected} голосовых каналов")
        
        # Закрываем соединение с БД
        if hasattr(self, 'db'):
            self.db.close()
        
        await super().close()
        logger.success("Бот завершил работу", "👋")