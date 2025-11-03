import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl
from core.logger import logger
import re
import os

class SimpleMusicPlayer:
    def __init__(self):
        self.queue = []
        self.current_track = None
        self.is_paused = False
        self.loop = False
        self.voice_client = None
    
    def add_to_queue(self, track):
        self.queue.append(track)
    
    def clear_queue(self):
        self.queue.clear()
        self.current_track = None
        self.is_paused = False
    
    def pause(self):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            self.is_paused = True
            return True
        return False
    
    def resume(self):
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            self.is_paused = False
            return True
        return False
    
    def stop(self):
        if self.voice_client:
            if self.voice_client.is_playing():
                self.voice_client.stop()
            self.clear_queue()
            return True
        return False

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.search_cache = {}
        logger.music("Музыкальный модуль с YouTube инициализирован")
        
        self.ydl_opts = {
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
        if query.startswith('https://'):
            if 'youtube.com' in query or 'youtu.be' in query:
                return 'youtube'
        return 'youtube'
    
    async def search_tracks(self, query, limit=10):
        """Поиск треков на YouTube"""
        try:
            logger.debug(f"Поиск на YouTube: '{query}'")
            
            with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                search_query = f"ytsearch{limit}:{query}"
                logger.debug(f"Поисковый запрос: {search_query}")
                
                data = await self.bot.loop.run_in_executor(
                    None, lambda: ydl.extract_info(search_query, download=False)
                )
            
            if not data:
                logger.warning(f"Нет данных от yt-dlp для запроса: {search_query}")
                return []
            
            tracks = []
            
            if 'entries' in data:
                for entry in data['entries']:
                    if entry and isinstance(entry, dict):
                        track = self._format_track_data(entry)
                        if track and track.get('url'):
                            tracks.append(track)
            elif isinstance(data, dict):
                track = self._format_track_data(data)
                if track and track.get('url'):
                    tracks.append(track)
            
            logger.debug(f"Найдено {len(tracks)} треков на YouTube для '{query}'")
            return tracks[:limit]
            
        except Exception as e:
            logger.error(f"Ошибка поиска на YouTube '{query}': {e}")
            return []
    
    def _format_track_data(self, entry):
        """Форматирует данные трека в универсальный формат"""
        try:
            title = entry.get('title', 'Неизвестно')
            uploader = entry.get('uploader', 'Неизвестно')
            
            # Чистим названия
            clean_patterns = [
                '(Official video)', '(Official Audio)', '(Official Music Video)', 
                '(Lyric Video)', '(Audio)', '(Lyrics)', '| Official Video'
            ]
            for pattern in clean_patterns:
                title = title.replace(pattern, '')
            title = title.strip()
            
            return {
                'title': title[:100],
                'url': entry.get('url'),
                'webpage_url': entry.get('webpage_url', ''),
                'duration': entry.get('duration', 0),
                'thumbnail': entry.get('thumbnail'),
                'uploader': uploader[:50],
                'platform': 'youtube'
            }
        except Exception as e:
            logger.error(f"Ошибка форматирования трека: {e}")
            return None
    
    async def get_track(self, url):
        """Получает информацию о конкретном треке"""
        try:
            logger.debug(f"Получение трека с YouTube: {url[:50]}...")
            
            with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                data = await self.bot.loop.run_in_executor(
                    None, lambda: ydl.extract_info(url, download=False)
                )
            
            if not data:
                raise Exception("Не удалось загрузить трек")
            
            track = self._format_track_data(data)
            if not track:
                raise Exception("Неверный формат данных трека")
            
            logger.debug(f"Успешно загружен трек с YouTube: '{track['title']}'")
            return track
            
        except Exception as e:
            error_msg = str(e)
            if "Sign in to confirm your age" in error_msg:
                logger.warning(f"Возрастное ограничение для трека: {url}")
                raise Exception("❌ Этот трек имеет возрастные ограничения и не может быть воспроизведен")
            else:
                logger.error(f"Ошибка загрузки трека с YouTube '{url}': {e}")
                raise Exception(f"Не удалось загрузить трек: {str(e)[:100]}")
    
    class TrackSelect(discord.ui.Select):
        def __init__(self, tracks, cog):
            self.tracks = tracks
            self.cog = cog
            
            options = []
            for i, track in enumerate(tracks[:10]):
                title = track['title']
                if len(title) > 90:
                    title = title[:87] + "..."
                
                options.append(
                    discord.SelectOption(
                        label=f"{i+1}. {title[:90]}",
                        description=f"{track['uploader']} | {cog.format_time(track['duration'])}",
                        value=str(i),
                        emoji="🎵"
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
            
            embed = discord.Embed(
                title="✅ Трек выбран",
                description=f"🎵 **{selected_track['title']}**\n🎤 {selected_track['uploader']}",
                color=0x00ff00
            )
            
            try:
                await interaction.edit_original_response(embed=embed, view=None)
            except discord.NotFound:
                await interaction.followup.send(embed=embed, ephemeral=True)
            
            await self.cog.play_selected_track(interaction, selected_track)
    
    class TrackView(discord.ui.View):
        def __init__(self, tracks, cog):
            super().__init__(timeout=60)
            self.add_item(MusicCog.TrackSelect(tracks, cog))
    
    @app_commands.command(name="play", description="Найти и выбрать музыку для воспроизведения")
    @app_commands.describe(query="Название трека или исполнителя")
    async def play(self, interaction: discord.Interaction, query: str):
        """Ищет музыку и позволяет выбрать из результатов"""
        await interaction.response.defer()
        
        if not interaction.user.voice:
            return await interaction.followup.send("❌ Подключись к голосовому каналу!")
        
        try:
            tracks = await self.search_tracks(query, limit=10)
            
            if not tracks:
                return await interaction.followup.send(
                    f"❌ Не найдено треков по запросу **'{query}'**\n\n"
                    f"💡 **Попробуй:**\n"
                    f"• Изменить запрос\n"
                    f"• Использовать более точное название\n"
                    f"• Проверить написание"
                )
            
            embed = discord.Embed(
                title=f"🎵 Результаты поиска на YouTube",
                description=f"Запрос: **{query}**\nНайдено **{len(tracks)}** треков. Выбери один из списка:",
                color=0x0099ff
            )
            
            for i, track in enumerate(tracks[:5], 1):
                embed.add_field(
                    name=f"{i}. {track['title'][:80]}",
                    value=f"🎤 {track['uploader']} | ⏱️ {self.format_time(track['duration'])}",
                    inline=False
                )
            
            if len(tracks) > 5:
                embed.set_footer(text=f"И еще {len(tracks) - 5} треков...")
            
            view = self.TrackView(tracks, self)
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Ошибка поиска с выбором: {e}")
            await interaction.followup.send(
                f"❌ Ошибка при поиске\n"
                f"**Попробуй:**\n"
                f"• Проверить интернет-соединение\n"
                f"• Попробовать позже\n"
                f"• Использовать другой запрос"
            )
    
    @app_commands.command(name="pause", description="Приостановить воспроизведение")
    async def pause(self, interaction: discord.Interaction):
        """Приостанавливает текущий трек"""
        try:
            player = self.bot.players.get(interaction.guild.id)
            if not player or not player.voice_client:
                return await interaction.response.send_message("❌ Сейчас ничего не играет", ephemeral=True)
            
            if player.is_paused:
                return await interaction.response.send_message("❌ Воспроизведение уже на паузе", ephemeral=True)
            
            if player.pause():
                await interaction.response.send_message("⏸️ Воспроизведение приостановлено")
                logger.music(f"Воспроизведение приостановлено на сервере: {interaction.guild.name}")
            else:
                await interaction.response.send_message("❌ Не удалось поставить на паузу", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Ошибка при паузе: {e}")
            await interaction.response.send_message("❌ Ошибка при попытке поставить на паузу", ephemeral=True)
    
    @app_commands.command(name="resume", description="Возобновить воспроизведение")
    async def resume(self, interaction: discord.Interaction):
        """Возобновляет воспроизведение"""
        try:
            player = self.bot.players.get(interaction.guild.id)
            if not player or not player.voice_client:
                return await interaction.response.send_message("❌ Сейчас ничего не играет", ephemeral=True)
            
            if not player.is_paused:
                return await interaction.response.send_message("❌ Воспроизведение не на паузе", ephemeral=True)
            
            if player.resume():
                await interaction.response.send_message("▶️ Воспроизведение возобновлено")
                logger.music(f"Воспроизведение возобновлено на сервере: {interaction.guild.name}")
            else:
                await interaction.response.send_message("❌ Не удалось возобновить воспроизведение", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Ошибка при возобновлении: {e}")
            await interaction.response.send_message("❌ Ошибка при попытке возобновить воспроизведение", ephemeral=True)
    
    @app_commands.command(name="stop", description="Остановить воспроизведение и очистить очередь")
    async def stop(self, interaction: discord.Interaction):
        """Полностью останавливает музыку и очищает очередь"""
        try:
            player = self.bot.players.get(interaction.guild.id)
            if not player or not player.voice_client:
                return await interaction.response.send_message("❌ Сейчас ничего не играет", ephemeral=True)
            
            if player.stop():
                await interaction.response.send_message("⏹️ Воспроизведение остановлено, очередь очищена")
                logger.music(f"Воспроизведение остановлено на сервере: {interaction.guild.name}")
            else:
                await interaction.response.send_message("❌ Не удалось остановить воспроизведение", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Ошибка при остановке: {e}")
            await interaction.response.send_message("❌ Ошибка при попытке остановить воспроизведение", ephemeral=True)
    
    @app_commands.command(name="skip", description="Пропустить текущий трек")
    async def skip(self, interaction: discord.Interaction):
        """Пропускает текущий трек"""
        try:
            player = self.bot.players.get(interaction.guild.id)
            if not player or not player.voice_client:
                return await interaction.response.send_message("❌ Сейчас ничего не играет", ephemeral=True)
            
            voice_client = interaction.guild.voice_client
            if voice_client and voice_client.is_playing():
                voice_client.stop()
                await interaction.response.send_message("⏭️ Трек пропущен")
                logger.music(f"Трек пропущен на сервере: {interaction.guild.name}")
            else:
                await interaction.response.send_message("❌ Сейчас ничего не играет", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Ошибка при пропуске трека: {e}")
            await interaction.response.send_message("❌ Ошибка при попытке пропустить трек", ephemeral=True)
    
    @app_commands.command(name="queue", description="Показать текущую очередь")
    async def queue(self, interaction: discord.Interaction):
        """Показывает текущую очередь треков"""
        try:
            player = self.bot.players.get(interaction.guild.id)
            if not player or not player.queue:
                return await interaction.response.send_message("📭 Очередь пуста", ephemeral=True)
            
            embed = discord.Embed(
                title="📋 Очередь воспроизведения",
                color=0x0099ff
            )
            
            # Текущий трек
            if player.current_track:
                embed.add_field(
                    name="🎵 Сейчас играет",
                    value=f"**{player.current_track['title']}**\n"
                          f"🎤 {player.current_track.get('uploader', 'Неизвестно')} | "
                          f"⏱️ {self.format_time(player.current_track.get('duration', 0))}",
                    inline=False
                )
            
            # Следующие треки в очереди
            if player.queue:
                queue_text = ""
                for i, track in enumerate(player.queue[:10], 1):
                    queue_text += f"**{i}.** {track['title'][:50]} - {self.format_time(track.get('duration', 0))}\n"
                
                if len(player.queue) > 10:
                    queue_text += f"\n... и еще {len(player.queue) - 10} треков"
                
                embed.add_field(
                    name=f"📜 Следующие треки ({len(player.queue)})",
                    value=queue_text,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Ошибка при показе очереди: {e}")
            await interaction.response.send_message("❌ Ошибка при получении очереди", ephemeral=True)
    
    async def play_selected_track(self, interaction, track_data):
        """Воспроизводит выбранный трек"""
        try:
            # Сначала получаем полную информацию о треке
            try:
                full_track = await self.get_track(track_data['webpage_url'] or track_data['url'])
                track_data.update(full_track)  # Обновляем данные трека
            except Exception as e:
                logger.warning(f"Не удалось получить полную информацию о треке: {e}")
                # Продолжаем с исходными данными
            
            track_data['requester'] = interaction.user
            
            player = self.bot.players.get(interaction.guild.id)
            if not player:
                player = SimpleMusicPlayer()
                self.bot.players[interaction.guild.id] = player
                logger.music(f"Создан новый плеер для сервера: {interaction.guild.name}")
            
            voice_client = interaction.guild.voice_client
            
            if voice_client:
                if voice_client.channel != interaction.user.voice.channel:
                    await voice_client.move_to(interaction.user.voice.channel)
                    logger.voice(f"Перемещен в канал: {interaction.user.voice.channel.name}")
            else:
                voice_client = await interaction.user.voice.channel.connect()
                logger.voice(f"Подключен к каналу: {interaction.user.voice.channel.name}")
            
            # Сохраняем voice_client в плеере
            player.voice_client = voice_client
            
            player.add_to_queue(track_data)
            queue_position = len(player.queue)
            
            logger.music(f"Добавлен в очередь: '{track_data['title']}' | Позиция: {queue_position}")
            
            if not voice_client.is_playing() and not voice_client.is_paused():
                await self.play_next(interaction.guild.id, voice_client)
                embed = self.create_track_embed(track_data)
                await interaction.followup.send(embed=embed)
                logger.music(f"Начато воспроизведение: '{track_data['title']}'")
            else:
                await interaction.followup.send(
                    f"🎵 Добавлено в очередь: **{track_data['title']}**\n"
                    f"📍 Позиция в очереди: {queue_position}"
                )
                
        except Exception as e:
            logger.error(f"Ошибка воспроизведения выбранного трека: {e}")
            error_msg = str(e)
            if "возрастные ограничения" in error_msg.lower():
                await interaction.followup.send("❌ Этот трек имеет возрастные ограничения и не может быть воспроизведен")
            else:
                await interaction.followup.send(f"❌ Ошибка: {error_msg[:100]}")

    def create_track_embed(self, track):
        embed = discord.Embed(
            title="🎵 Сейчас играет",
            description=f"**{track['title']}**",
            color=0x00ff00
        )
        embed.add_field(name="Длительность", value=self.format_time(track.get('duration', 0)), inline=True)
        embed.add_field(name="Исполнитель", value=track.get('uploader', 'Неизвестно'), inline=True)
        embed.add_field(name="Платформа", value="YouTube", inline=True)
        
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
            logger.music(f"🎵 Начато воспроизведение: '{track['title']}' | Сервер: {guild_id}")
            
        except Exception as e:
            logger.error(f"Ошибка воспроизведения трека '{track['title']}': {e}")
            await asyncio.sleep(2)
            await self.play_next(guild_id, voice_client)

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
    logger.success("Музыкальный модуль с YouTube загружен", "🎵")