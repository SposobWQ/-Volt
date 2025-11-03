# Создайте файл youtube_fix.py
import yt_dlp as youtube_dl
import os

def test_youtube_fix():
    """Тестирует различные методы обхода блокировки"""
    
    # Метод 1: С пользовательскими headers
    opts1 = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        'socket_timeout': 30,
        'retries': 5,
        'extract_flat': False,
        'force_ipv4': True,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'http_headers': {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Mode': 'navigate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    
    # Метод 2: С имитацией браузера
    opts2 = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        'socket_timeout': 30,
        'retries': 5,
        'extract_flat': False,
        'force_ipv4': True,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'referer': 'https://www.youtube.com/',
    }
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley
    
    for i, opts in enumerate([opts1, opts2], 1):
        print(f"\n🔧 Тестируем метод {i}...")
        try:
            with youtube_dl.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(test_url, download=False)
                if info:
                    print(f"✅ Метод {i} РАБОТАЕТ!")
                    print(f"   Трек: {info.get('title', 'N/A')}")
                    return opts
                else:
                    print(f"❌ Метод {i} не сработал")
        except Exception as e:
            print(f"❌ Метод {i} ошибка: {e}")
    
    return None

if __name__ == "__main__":
    print("🎵 Тестирование обхода блокировки YouTube...")
    working_opts = test_youtube_fix()
    if working_opts:
        print(f"\n🎉 Используйте эти настройки в music.py!")