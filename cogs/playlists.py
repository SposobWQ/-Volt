import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import json
from datetime import datetime
from utils.music_classes import AdvancedMusicPlayer, AdvancedTrack


class PlaylistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="playlist_create", description="Создать новый плейлист")
    @app_commands.describe(name="Название плейлиста")
    async def playlist_create(self, interaction: discord.Interaction, name: str):
        """Создает новый плейлист для пользователя"""
        try:
            cursor = self.bot.db.conn.cursor()
            
            # Проверяем, существует ли уже плейлист с таким именем
            cursor.execute(
                'SELECT id FROM playlists WHERE user_id = ? AND guild_id = ? AND name = ?',
                (str(interaction.user.id), str(interaction.guild.id), name)
            )
            
            if cursor.fetchone():
                return await interaction.response.send_message(
                    f"❌ Плейлист с названием `{name}` уже существует",
                    ephemeral=True
                )
            
            # Создаем новый плейлист
            cursor.execute(
                'INSERT INTO playlists (user_id, guild_id, name) VALUES (?, ?, ?)',
                (str(interaction.user.id), str(interaction.guild.id), name)
            )
            self.bot.db.conn.commit()
            
            await interaction.response.send_message(
                f"✅ Плейлист `{name}` успешно создан!",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ошибка при создании плейлиста: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="playlist_add", description="Добавить трек в плейлист")
    @app_commands.describe(
        playlist_name="Название плейлиста",
        query="Название трека или URL"
    )
    async def playlist_add(self, interaction: discord.Interaction, playlist_name: str, query: str):
        """Добавляет трек в указанный плейлист"""
        await interaction.response.defer()
        
        try:
            # Получаем плейлист
            cursor = self.bot.db.conn.cursor()
            cursor.execute(
                'SELECT id FROM playlists WHERE user_id = ? AND guild_id = ? AND name = ?',
                (str(interaction.user.id), str(interaction.guild.id), playlist_name)
            )
            
            playlist = cursor.fetchone()
            if not playlist:
                return await interaction.followup.send(
                    f"❌ Плейлист `{playlist_name}` не найден"
                )
            
            playlist_id = playlist[0]
            
            # Получаем информацию о треке
            music_cog = self.bot.get_cog('MusicCog')
            if not music_cog:
                return await interaction.followup.send("❌ Музыкальный модуль не загружен")
            
            track_data = await music_cog.get_track(query)
            
            # Добавляем трек в плейлист
            cursor.execute(
                '''INSERT INTO playlist_tracks 
                (playlist_id, title, url, duration, thumbnail, platform) 
                VALUES (?, ?, ?, ?, ?, ?)''',
                (playlist_id, track.title, track.url, track.duration, 
                 track.thumbnail, track.platform)
            )
            self.bot.db.conn.commit()
            
            await interaction.followup.send(
                f"✅ Трек **{track.title}** добавлен в плейлист `{playlist_name}`"
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Ошибка: {str(e)}")
    
    @app_commands.command(name="playlist_list", description="Показать все плейлисты")
    async def playlist_list(self, interaction: discord.Interaction):
        """Показывает все плейлисты пользователя"""
        try:
            cursor = self.bot.db.conn.cursor()
            cursor.execute(
                '''SELECT p.name, COUNT(pt.id) as track_count, p.created_at
                FROM playlists p 
                LEFT JOIN playlist_tracks pt ON p.id = pt.playlist_id
                WHERE p.user_id = ? AND p.guild_id = ?
                GROUP BY p.id, p.name
                ORDER BY p.created_at DESC''',
                (str(interaction.user.id), str(interaction.guild.id))
            )
            
            playlists = cursor.fetchall()
            
            if not playlists:
                return await interaction.response.send_message(
                    "📭 У вас пока нет плейлистов. Создайте первый с помощью `/playlist_create`",
                    ephemeral=True
                )
            
            embed = discord.Embed(
                title="📋 Ваши плейлисты",
                color=0x0099ff
            )
            
            for name, track_count, created_at in playlists:
                embed.add_field(
                    name=f"🎵 {name}",
                    value=f"Треков: {track_count}\nСоздан: {created_at[:10]}",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ошибка при загрузке плейлистов: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="playlist_play", description="Воспроизвести плейлист")
    @app_commands.describe(playlist_name="Название плейлиста")
    async def playlist_play(self, interaction: discord.Interaction, playlist_name: str):
        """Добавляет все треки из плейлиста в очередь"""
        await interaction.response.defer()
        
        if not interaction.user.voice:
            return await interaction.followup.send("❌ Подключитесь к голосовому каналу!")
        
        try:
            # Получаем плейлист и треки
            cursor = self.bot.db.conn.cursor()
            cursor.execute(
                '''SELECT pt.title, pt.url, pt.duration, pt.thumbnail, pt.platform
                FROM playlists p
                JOIN playlist_tracks pt ON p.id = pt.playlist_id
                WHERE p.user_id = ? AND p.guild_id = ? AND p.name = ?
                ORDER BY pt.added_at''',
                (str(interaction.user.id), str(interaction.guild.id), playlist_name)
            )
            
            tracks = cursor.fetchall()
            
            if not tracks:
                return await interaction.followup.send( 
                    f"❌ Плейлист `{playlist_name}` не найден или пуст"
                )
            
            # Получаем или создаем плеер
            player = self.bot.players.get(interaction.guild.id)
            if not player:
                player = AdvancedMusicPlayer()
                self.bot.players[interaction.guild.id] = player
            
            # Подключаемся к голосовому каналу
            voice_client = interaction.guild.voice_client
            if not voice_client:
                voice_client = await interaction.user.voice.channel.connect()
            
            # Добавляем треки в очередь
            added_count = 0
            for title, url, duration, thumbnail, platform in tracks:
                track_data = {
                    'title': title,
                    'url': url,
                    'duration': duration,
                    'thumbnail': thumbnail,
                    'uploader': 'Плейлист',
                    'extractor': platform
                }
                track_data['requester'] = interaction.user
                player.add_to_queue(track_data)
                added_count += 1
            
            # Запускаем воспроизведение если ничего не играет
            if not voice_client.is_playing() and not player.is_paused:
                music_cog = self.bot.get_cog('MusicCog')
                if music_cog:
                    await music_cog.play_next(interaction.guild.id, voice_client)
            
            await interaction.followup.send(
                f"✅ Добавлено **{added_count}** треков из плейлиста `{playlist_name}` в очередь"
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Ошибка: {str(e)}")

async def setup(bot):
    await bot.add_cog(PlaylistCog(bot))