"""
Ядро бота - основные классы и конфигурация
"""
from .bot import PerfectMusicBot
from .database import Database
from .permissions import PermissionSystem
from .config import Config
from .logger import logger

__all__ = ['PerfectMusicBot', 'Database', 'PermissionSystem', 'Config', 'logger']