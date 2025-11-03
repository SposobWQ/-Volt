# core/config.py
import os

class Config:
    # Путь к ffmpeg
    FFMPEG_PATH = None
    
    # Автоматически определяем путь к ffmpeg
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'ffmpeg', 'bin', 'ffmpeg.exe'),
        os.path.join(os.path.dirname(__file__), '..', 'ffmpeg', 'bin', 'ffmpeg'),
        os.path.join(os.path.dirname(__file__), '..', 'ffmpeg', 'ffmpeg.exe'),
        os.path.join(os.path.dirname(__file__), '..', 'ffmpeg', 'ffmpeg'),
        'ffmpeg',  # Системный ffmpeg
        'ffmpeg.exe',  # Системный ffmpeg (Windows)
    ]
    
    for path in possible_paths:
        abs_path = os.path.abspath(path) if not path.startswith('ffmpeg') else path
        if os.path.exists(abs_path) if not path.startswith('ffmpeg') else os.system(f"{path} -version >nul 2>&1") == 0:
            FFMPEG_PATH = abs_path
            break
    
    # Настройки YouTube DL
    YDL_OPTIONS = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        'default_search': 'ytsearch:',
        'extractaudio': True,
        'audioformat': 'mp3',
        'socket_timeout': 10,
        'nopart': True,
    }
    
    # Настройки FFmpeg с правильным путем
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
        'options': '-vn -filter:a "volume=0.8"'
    }
    
    # Настройки бота
    DEFAULT_PREFIX = '!'
    EMBED_COLOR = 0x00ff00