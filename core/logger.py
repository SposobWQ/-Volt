import logging
import sys
from datetime import datetime
import os

class BotLogger:
    def __init__(self):
        self.logger = logging.getLogger('music_bot')
        self.logger.setLevel(logging.INFO)
        
        # Форматтер с цветами и временем
        self._setup_logging()
    
    def _setup_logging(self):
        """Настройка системы логирования"""
        if self.logger.handlers:
            return
            
        # Создаем папку для логов если нет
        os.makedirs('logs', exist_ok=True)
        
        # Формат для консоли
        console_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Формат для файла
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Консольный handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_format)
        
        # Файловый handler
        file_handler = logging.FileHandler(
            f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_format)
        
        # Добавляем handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message, emoji="ℹ️"):
        """Информационное сообщение"""
        self.logger.info(f"{emoji} {message}")
    
    def success(self, message, emoji="✅"):
        """Сообщение об успехе"""
        self.logger.info(f"{emoji} {message}")
    
    def warning(self, message, emoji="⚠️"):
        """Предупреждение"""
        self.logger.warning(f"{emoji} {message}")
    
    def error(self, message, emoji="❌"):
        """Ошибка"""
        self.logger.error(f"{emoji} {message}")
    
    def debug(self, message, emoji="🐛"):
        """Отладочное сообщение"""
        self.logger.debug(f"{emoji} {message}")
    
    def command(self, user, command, guild=None, emoji="🎮"):
        """Логирование команд"""
        guild_info = f" | Сервер: {guild}" if guild else ""
        self.logger.info(f"{emoji} Команда: {command} | Пользователь: {user}{guild_info}")
    
    def music(self, message, emoji="🎵"):
        """Логирование музыкальных событий"""
        self.logger.info(f"{emoji} {message}")
    
    def voice(self, message, emoji="🔊"):
        """Логирование голосовых событий"""
        self.logger.info(f"{emoji} {message}")
    
    def database(self, message, emoji="💾"):
        """Логирование операций с БД"""
        self.logger.info(f"{emoji} {message}")

# Глобальный экземпляр логгера
logger = BotLogger()