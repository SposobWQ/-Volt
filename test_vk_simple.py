import yt_dlp as youtube_dl

def test_platform(platform, query):
    """Тестирует поиск на разных платформах"""
    print(f"\n🔍 Тестируем {platform}: '{query}'")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            search_queries = {
                'youtube': f'ytsearch3:{query}',
                'vkontakte': f'vksearch3:{query}',
                'yandex': f'ymsearch3:{query}',
                'zaycev': f'zaycevsearch3:{query}',
                'rutube': f'rutubesearch3:{query}',
            }
            
            if platform in search_queries:
                data = ydl.extract_info(search_queries[platform], download=False)
                
                if data and 'entries' in data:
                    print(f"✅ Найдено {len(data['entries'])} треков:")
                    for i, entry in enumerate(data['entries'][:2], 1):
                        if entry:
                            title = entry.get('title', 'N/A')[:60]
                            print(f"   {i}. {title}")
                else:
                    print("❌ Не найдено результатов")
            else:
                print("⚠️  Платформа не поддерживается")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# Тестируем русские треки на разных платформах
test_songs = ["Макс Корж", "Баста", "Rammstein", "Billie Eilish"]

for song in test_songs:
    print(f"\n{'='*50}")
    print(f"🎵 ТЕСТ: {song}")
    print('='*50)
    
    test_platform('vkontakte', song)
    test_platform('yandex', song)
    test_platform('zaycev', song)
    test_platform('youtube', song)