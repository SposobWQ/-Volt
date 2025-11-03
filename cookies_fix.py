import yt_dlp as youtube_dl

def test_age_restricted_video():
    """Тестирует обход возрастных ограничений"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,
        'socket_timeout': 30,
        'retries': 3,
        'age_limit': 0,  # Игнорировать возрастные ограничения
    }
    
    # Тестовые URL с возрастными ограничениями
    test_urls = [
        "https://www.youtube.com/watch?v=X5YU9SgpXNo",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley
    ]
    
    for url in test_urls:
        print(f"\n🔍 Тестируем URL: {url}")
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                data = ydl.extract_info(url, download=False)
            
            if data:
                print(f"✅ УСПЕХ: Трек доступен")
                print(f"   Название: {data.get('title', 'N/A')}")
                print(f"   Длительность: {data.get('duration', 'N/A')}")
                print(f"   URL аудио: {data.get('url', 'N/A')[:80]}...")
            else:
                print("❌ Не удалось получить данные")
                
        except Exception as e:
            error_msg = str(e)
            if "Sign in to confirm your age" in error_msg:
                print("❌ ВОЗРАСТНОЕ ОГРАНИЧЕНИЕ: Требуется авторизация")
                print("💡 Решение: Используйте другой трек или платформу")
            else:
                print(f"❌ ОШИБКА: {error_msg[:100]}")

if __name__ == "__main__":
    print("🔧 Тестирование обхода возрастных ограничений YouTube")
    print("=" * 60)
    test_age_restricted_video()