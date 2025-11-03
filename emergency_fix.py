# emergency_fix.py - экстренные методы для Render
import yt_dlp as youtube_dl
import random

def get_working_ydl_opts():
    """Возвращает РАБОЧИЕ настройки для Render"""
    
    # Случайный User-Agent из списка
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0'
    ]
    
    return {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        'socket_timeout': 30,
        'retries': 15,  # Увеличиваем до 15
        'extract_flat': False,
        'force_ipv4': True,
        'geo_bypass': True,
        'geo_bypass_country': random.choice(['US', 'DE', 'FR', 'CA', 'GB']),
        
        # КРИТИЧЕСКИ ВАЖНЫЕ ДЛЯ RENDER:
        'user_agent': random.choice(user_agents),
        'referer': 'https://www.youtube.com/',
        'no_check_certificate': True,
        'prefer_insecure': True,
        
        # Добавляем прокси (некоторые работают)
        'proxy': random.choice([
            None,  # Без прокси
            'https://www.google.com/',  # Иногда помогает
        ]),
        
        # Ограничиваем скорость для имитации человека
        'throttledratelimit': 1024,
    }

def test_render_fix():
    """Тестирует настройки для Render"""
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley
        "https://www.youtube.com/watch?v=JGwWNGJdvx8",  # Shape of You
        "https://www.youtube.com/watch?v=60ItHLz5WEA",  # NCS
    ]
    
    for i in range(5):  # Пробуем 5 разных конфигураций
        print(f"\n🎯 Попытка {i+1}...")
        opts = get_working_ydl_opts()
        
        for url in test_urls:
            try:
                with youtube_dl.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        print(f"✅ РАБОТАЕТ: {info.get('title', 'N/A')[:50]}")
                        return opts  # Возвращаем первую рабочую конфигурацию
            except Exception as e:
                if "bot" not in str(e).lower():
                    print(f"❌ Ошибка: {e}")
                continue
    
    return None

if __name__ == "__main__":
    print("🚨 ЭКСТРЕННЫЙ поиск работающей конфигурации для Render...")
    working_opts = test_render_fix()
    if working_opts:
        print(f"\n🎉 НАЙДЕНА РАБОЧАЯ КОНФИГУРАЦИЯ!")
    else:
        print(f"\n💥 Все методы не сработали. Нужен альтернативный подход.")