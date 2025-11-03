import discord
import re
from datetime import datetime

def format_time(seconds):
    """Форматирует время в читаемый формат"""
    if not seconds:
        return "Неизвестно"
    
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

def create_embed(title, description="", color=0x00ff00, **kwargs):
    """Создает стандартизированный embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    
    if 'fields' in kwargs:
        for name, value, inline in kwargs['fields']:
            embed.add_field(name=name, value=value, inline=inline)
    
    if 'footer' in kwargs:
        embed.set_footer(text=kwargs['footer'])
    
    if 'thumbnail' in kwargs:
        embed.set_thumbnail(url=kwargs['thumbnail'])
    
    if 'image' in kwargs:
        embed.set_image(url=kwargs['image'])
    
    return embed

def validate_url(url):
    """Проверяет валидность URL для музыкальных платформ"""
    patterns = [
        r'(https?://)?(www\.)?(youtube|youtu)\.(com|be)/.+',
        r'(https?://)?(www\.)?soundcloud\.com/.+',
        r'(https?://)?(www\.)?spotify\.com/.+',
        r'(https?://)?(www\.)?vk\.com/.+'
    ]
    
    return any(re.match(pattern, url) for pattern in patterns)

def parse_time(time_str):
    """Парсит строку времени в секунды"""
    try:
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:  # MM:SS
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:  # HH:MM:SS
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        else:
            return int(time_str)  # Считаем что это секунды
    except:
        return None

def truncate_text(text, max_length=100):
    """Обрезает текст до максимальной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def get_user_avatar(user):
    """Возвращает аватар пользователя или стандартный"""
    return user.avatar.url if user.avatar else user.default_avatar.url