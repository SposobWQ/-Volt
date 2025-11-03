import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl
from core.logger import logger
import re

class SimpleMusicPlayer:
    def __init__(self):
        self.queue = []
        self.current_track = None
        self.is_paused = False
        self.loop = False
    
    def add_to_queue(self, track):
        self.queue.append(track)
    
    def clear_queue(self):
        self.queue.clear()
        self.current_track = None

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.search_cache = {}
        logger.music("Музыкальный модуль инициализирован")
        
        # Настройки для разных платформ
        self.platform_configs = {
            'youtube': {
                'name': 'YouTube',
                'emoji': '📺',
                'search_prefix': 'ytsearch:',
                'ydl_opts': {
                    'format': 'bestaudio/best',
                    'noplaylist': True,
                    'nocheckcertificate': True,
                    'ignoreerrors': True,
                    'no_warnings': True,
                    'quiet': True,
                    'extractaudio': True,
                    'audioformat': 'mp3',
                }
            },
            'vkontakte': {
                'name': 'VK Музыка',
                'emoji': '🔵', 
                'search_prefix': 'vksearch:',
                'ydl_opts': {
                    'format': 'bestaudio/best',
                    'noplaylist': True,
                    'nocheckcertificate': True,
                    'ignoreerrors': True,
                    'no_warnings': True,
                    'quiet': True,
                    'extractaudio': True,
                    'audioformat': 'mp3',
                    'extractor_args': {
                        'vk:access_token': 'your_vk_token_here'  # Нужно будет настроить
                    }
                }
            },
            'soundcloud': {
                'name': 'SoundCloud',
                'emoji': '🎧',
                'search_prefix': 'scsearch:',
                'ydl_opts': {
                    'format': 'bestaudio/best',
                    'noplaylist': True,
                    'nocheckcertificate': True,
                    'ignoreerrors': True,
                    'no_warnings': True,
                    'quiet': True,
                    'extractaudio': True,
                    'audioformat': 'mp3',
                }
            }
        }
    
    def format_time(self, seconds):
        """Форматирует время в читаемый формат"""
        if not seconds:
            return "Неизвестно"
        
        seconds = int(seconds)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
    
    def detect_platform(self, query):
        """Автоматически определяет платформу по запросу"""
        # Если это URL, определяем платформу
        if query.startswith('https://'):
            if 'youtube.com' in query or 'youtu.be' in query:
                return 'youtube'
            elif 'vk.com' in query or 'vkontakte' in query:
                return 'vkontakte'
            elif 'soundcloud.com' in query:
                return 'soundcloud'
        
        # По умолчанию используем YouTube для поиска
        return 'youtube'
    
    async def search_tracks(self, query, platform='youtube', limit=10):
        """Поиск треков на выбранной платформе"""
        try:
            logger.debug(f"Поиск на {platform}: '{query}'")
            
            config = self.platform_configs.get(platform, self.platform_configs['youtube'])
            
            # Для VK нужно специальная обработка
            if platform == 'vkontakte':
                return await self.search_vk_music(query, limit)
            
            ydl_opts = config['ydl_opts'].copy()
            ydl_opts['default_search'] = f"{config['search_prefix']}{limit}"
            
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                search_query = f"{config['search_prefix']}{limit}:{query}"
                data = await self.bot.loop.run_in_executor(
                    None, lambda: ydl.extract_info(search_query, download=False)
                )
            
            if not data or 'entries' not in data:
                return []
            
            tracks = []
            for entry in data['entries']:
                if entry and isinstance(entry, dict):
                    tracks.append({
                        'title': entry.get('title', 'Неизвестно'),
                        'url': entry.get('url'),
                        'webpage_url': entry.get('webpage_url', ''),
                        'duration': entry.get('duration', 0),
                        'thumbnail': entry.get('thumbnail'),
                        'uploader': entry.get('uploader', 'Неизвестно'),
                        'platform': platform
                    })
            
            logger.debug(f"Найдено {len(tracks)} треков на {platform} для '{query}'")
            return tracks[:limit]
            
        except Exception as e:
            logger.error(f"Ошибка поиска на {platform} '{query}': {e}")
            return []
    
    async def search_vk_music(self, query, limit=10):
        """Поиск музыки ВКонтакте (заглушка - нужно настроить токен)"""
        try:
            # Временная заглушка для VK
            # Для работы нужно получить access_token VK и настроить yt-dlp
            logger.warning("VK музыка требует настройки access_token")
            
            # Пока возвращаем пустой список
            return []
            
        except Exception as e:
            logger.error(f"Ошибка поиска VK: {e}")
            return []
    
    async def get_track(self, url, platform='youtube'):
        """Получает информацию о конкретном треке"""
        try:
            logger.debug(f"Получение трека с {platform}: {url[:50]}...")
            
            config = self.platform_configs.get(platform, self.platform_configs['youtube'])
            
            with youtube_dl.YoutubeDL(config['ydl_opts']) as ydl:
                data = await self.bot.loop.run_in_executor(
                    None, lambda: ydl.extract_info(url, download=False)
                )
            
            if not data:
                raise Exception("Не удалось загрузить трек")
            
            track = {
                'title': data.get('title', 'Неизвестно'),
                'url': data.get('url'),
                'webpage_url': data.get('webpage_url', url),
                'duration': data.get('duration', 0),
                'thumbnail': data.get('thumbnail'),
                'uploader': data.get('uploader', 'Неизвестно'),
                'platform': platform
            }
            
            logger.debug(f"Успешно загружен трек с {platform}: '{track['title']}'")
            return track
            
        except Exception as e:
            logger.error(f"Ошибка загрузки трека с {platform} '{url}': {e}")
            raise Exception(f"Не удалось загрузить трек: {str(e)}")
    
    class PlatformSelect(discord.ui.Select):
        def __init__(self, cog):
            self.cog = cog
            
            options = [
                discord.SelectOption(
                    label="📺 YouTube",
                    description="Поиск на YouTube",
                    value="youtube",
                    emoji="📺"
                ),
                discord.SelectOption(
                    label="🔵 VK Музыка", 
                    description="Поиск во ВКонтакте",
                    value="vkontakte",
                    emoji="🔵"
                ),
                discord.SelectOption(
                    label="🎧 SoundCloud",
                    description="Поиск на SoundCloud", 
                    value="soundcloud",
                    emoji="🎧"
                )
            ]
            
            super().__init__(
                placeholder="🌐 Выбери платформу для поиска...",
                min_values=1,
                max_values=1,
                options=options
            )
        
        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            # Сохраняем выбор платформы для этого пользователя
            self.cog.search_cache[f"{interaction.user.id}_platform"] = self.values[0]
            
            config = self.cog.platform_configs.get(self.values[0])
            await interaction.followup.send(
                f"{config['emoji']} Выбрана платформа: **{config['name']}**\n"
                f"Теперь введи `/play название_трека`",
                ephemeral=True
            )
    
    class PlatformView(discord.ui.View):
        def __init__(self, cog):
            super().__init__(timeout=30)
            self.add_item(MusicCog.PlatformSelect(cog))
    
    class TrackSelect(discord.ui.Select):
        def __init__(self, tracks, cog, platform):
            self.tracks = tracks
            self.cog = cog
            self.platform = platform
            
            options = []
            for i, track in enumerate(tracks[:10]):
                title = track['title']
                if len(title) > 90:
                    title = title[:87] + "..."
                
                platform_emoji = cog.platform_configs.get(track.get('platform', 'youtube'), {}).get('emoji', '🎵')
                
                options.append(
                    discord.SelectOption(
                        label=f"{i+1}. {title[:90]}",
                        description=f"{track['uploader']} | {cog.format_time(track['duration'])}",
                        value=str(i),
                        emoji=platform_emoji
                    )
                )
            
            super().__init__(
                placeholder="🎵 Выбери трек для воспроизведения...",
                min_values=1,
                max_values=1,
                options=options
            )
        
        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            
            selected_index = int(self.values[0])
            selected_track = self.tracks[selected_index]
            
            # Обновляем сообщение
            platform_emoji = self.cog.platform_configs.get(self.platform, {}).get('emoji', '🎵')
            embed = discord.Embed(
                title="✅ Трек выбран",
                description=f"{platform_emoji} **{selected_track['title']}**\n🎤 {selected_track['uploader']}",
                color=0x00ff00
            )
            await interaction.edit_original_response(embed=embed, view=None)
            
            # Добавляем трек в очередь и воспроизводим
            await self.cog.play_selected_track(interaction, selected_track)
    
    class TrackView(discord.ui.View):
        def __init__(self, tracks, cog, platform):
            super().__init__(timeout=60)
            self.add_item(MusicCog.TrackSelect(tracks, cog, platform))
    
    @app_commands.command(name="platform", description="Выбрать платформу для поиска музыки")
    async def platform(self, interaction: discord.Interaction):
        """Выбор платформы для поиска музыки"""
        view = self.PlatformView(self)
        embed = discord.Embed(
            title="🌐 Выбор платформы",
            description="Выбери платформу для поиска музыки:",
            color=0x0099ff
        )
        embed.add_field(name="📺 YouTube", value="Самая большая база музыки", inline=True)
        embed.add_field(name="🔵 VK Музыка", value="Русская музыка и популярные треки", inline=True) 
        embed.add_field(name="🎧 SoundCloud", value="Независимые исполнители", inline=True)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="play", description="Найти и выбрать музыку для воспроизведения")
    @app_commands.describe(
        query="Название трека или исполнителя",
        platform="Платформа для поиска (необязательно)"
    )
    async def play(self, interaction: discord.Interaction, query: str, platform: str = None):
        """Ищет музыку и позволяет выбрать из результатов"""
        await interaction.response.defer()
        
        if not interaction.user.voice:
            return await interaction.followup.send("❌ Подключись к голосовому каналу!")
        
        try:
            # Определяем платформу
            if not platform:
                # Пробуем определить автоматически или берем из кэша
                platform = self.search_cache.get(f"{interaction.user.id}_platform", "youtube")
            
            # Автоматическое определение платформы для URL
            auto_platform = self.detect_platform(query)
            if auto_platform != 'youtube':
                platform = auto_platform
            
            config = self.platform_configs.get(platform, self.platform_configs['youtube'])
            logger.debug(f"Поиск на {platform}: '{query}'")
            
            # Ищем треки
            tracks = await self.search_tracks(query, platform, limit=10)
            
            if not tracks:
                # Если на выбранной платформе нет результатов, пробуем YouTube
                if platform != 'youtube':
                    tracks = await self.search_tracks(query, 'youtube', limit=10)
                    if tracks:
                        platform = 'youtube'
                        config = self.platform_configs['youtube']
                
                if not tracks:
                    return await interaction.followup.send(
                        f"❌ Не найдено треков на {config['name']} по запросу '{query}'"
                    )
            
            # Создаем embed с результатами
            embed = discord.Embed(
                title=f"{config['emoji']} Результаты поиска на {config['name']}",
                description=f"Запрос: **{query}**\nНайдено **{len(tracks)}** треков. Выбери один из списка:",
                color=0x0099ff
            )
            
            # Показываем первые 5 треков в описании
            for i, track in enumerate(tracks[:5], 1):
                embed.add_field(
                    name=f"{i}. {track['title'][:80]}",
                    value=f"🎤 {track['uploader']} | ⏱️ {self.format_time(track['duration'])}",
                    inline=False
                )
            
            if len(tracks) > 5:
                embed.set_footer(text=f"И еще {len(tracks) - 5} треков...")
            
            # Создаем View с выбором
            view = self.TrackView(tracks, self, platform)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Ошибка поиска с выбором: {e}")
            await interaction.followup.send(f"❌ Ошибка поиска: {str(e)}")
    
    async def play_selected_track(self, interaction, track_data):
        """Воспроизводит выбранный трек"""
        try:
            track_data['requester'] = interaction.user
            
            player = self.bot.players.get(interaction.guild.id)
            if not player:
                player = SimpleMusicPlayer()
                self.bot.players[interaction.guild.id] = player
                logger.music(f"Создан новый плеер для сервера: {interaction.guild.name}")
            
            voice_client = interaction.guild.voice_client
            
            # Подключаемся к голосовому каналу
            if voice_client:
                if voice_client.channel != interaction.user.voice.channel:
                    await voice_client.move_to(interaction.user.voice.channel)
                    logger.voice(f"Перемещен в канал: {interaction.user.voice.channel.name}")
            else:
                voice_client = await interaction.user.voice.channel.connect()
                logger.voice(f"Подключен к каналу: {interaction.user.voice.channel.name}")
            
            # Добавляем трек в очередь
            player.add_to_queue(track_data)
            queue_position = len(player.queue)
            
            platform_emoji = self.platform_configs.get(track_data.get('platform', 'youtube'), {}).get('emoji', '🎵')
            logger.music(f"Добавлен в очередь: '{track_data['title']}' | Платформа: {track_data.get('platform', 'youtube')} | Позиция: {queue_position}")
            
            # Если ничего не играет и не на паузе - начинаем воспроизведение
            if not voice_client.is_playing() and not voice_client.is_paused():
                await self.play_next(interaction.guild.id, voice_client)
                embed = self.create_track_embed(track_data)
                await interaction.followup.send(embed=embed)
                logger.music(f"Начато воспроизведение: '{track_data['title']}'")
            else:
                await interaction.followup.send(
                    f"{platform_emoji} Добавлено в очередь: **{track_data['title']}**\n"
                    f"📍 Позиция в очереди: {queue_position}"
                )
                
        except Exception as e:
            logger.error(f"Ошибка воспроизведения выбранного трека: {e}")
            await interaction.followup.send(f"❌ Ошибка: {str(e)}")

    # ... остальные команды (pause, resume, stop, skip, queue, nowplaying) остаются без изменений ...

    def create_track_embed(self, track):
        platform_emoji = self.platform_configs.get(track.get('platform', 'youtube'), {}).get('emoji', '🎵')
        
        embed = discord.Embed(
            title=f"{platform_emoji} Сейчас играет",
            description=f"**{track['title']}**",
            color=0x00ff00
        )
        embed.add_field(name="Длительность", value=self.format_time(track.get('duration', 0)), inline=True)
        embed.add_field(name="Исполнитель", value=track.get('uploader', 'Неизвестно'), inline=True)
        embed.add_field(name="Платформа", value=self.platform_configs.get(track.get('platform', 'youtube'), {}).get('name', 'YouTube'), inline=True)
        
        if 'requester' in track:
            embed.add_field(name="Запросил", value=track['requester'].mention, inline=True)
        
        if track.get('thumbnail'):
            embed.set_thumbnail(url=track['thumbnail'])
            
        return embed
    
    async def play_next(self, guild_id, voice_client):
        """Воспроизводит следующий трек в очереди"""
        player = self.bot.players.get(guild_id)
        
        if not player or not player.queue:
            player.current_track = None
            logger.music(f"Очередь пуста | Сервер ID: {guild_id}")
            
            await asyncio.sleep(60)
            
            player = self.bot.players.get(guild_id)
            if not player or not player.queue:
                if voice_client and voice_client.is_connected():
                    await voice_client.disconnect()
                    logger.voice(f"Отключен из-за пустой очереди | Сервер ID: {guild_id}")
                if guild_id in self.bot.players:
                    del self.bot.players[guild_id]
            return
        
        track = player.queue.pop(0)
        player.current_track = track
        
        try:
            if not voice_client or not voice_client.is_connected():
                logger.warning("Голосовое соединение разорвано")
                return
                
            ffmpeg_options = {
                'executable': r'C:\ffmpeg\bin\ffmpeg.exe',
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
                'options': '-vn -af "volume=0.8"'
            }
            
            source = discord.FFmpegPCMAudio(
                track['url'],
                **ffmpeg_options
            )
            
            def after_play(error):
                if error:
                    logger.error(f"Ошибка воспроизведения: {error}")
                
                coro = self.play_next(guild_id, voice_client)
                asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
            
            voice_client.play(source, after=after_play)
            platform_emoji = self.platform_configs.get(track.get('platform', 'youtube'), {}).get('emoji', '🎵')
            logger.music(f"{platform_emoji} Начато воспроизведение: '{track['title']}' | Сервер: {guild_id}")
            
        except Exception as e:
            logger.error(f"Ошибка воспроизведения трека '{track['title']}': {e}")
            await asyncio.sleep(2)
            await self.play_next(guild_id, voice_client)

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
    logger.success("Музыкальный модуль с поддержкой платформ загружен", "🎵")