# core/config.py
class Config:
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
    
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
        'options': '-vn -filter:a "volume=0.8"'
    }
    
    # Настройки бота
    DEFAULT_PREFIX = '!'
    EMBED_COLOR = 0x00ff00