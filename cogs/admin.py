import discord
from discord import app_commands
from discord.ext import commands
import json
from datetime import datetime

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="music_setup", description="Настройка музыкальной системы")
    @app_commands.describe(
        admin_roles="Роли администраторов (через запятую)",
        dj_roles="Роли DJ (через запятую)", 
        max_queue_size="Максимальный размер очереди",
        default_volume="Громкость по умолчанию (0.1-1.0)"
    )
    async def music_setup(self, interaction: discord.Interaction,
                         admin_roles: str = None,
                         dj_roles: str = None,
                         max_queue_size: int = 100,
                         default_volume: float = 0.8):
        """Настройка параметров музыки для сервера"""
        
        # Проверяем права
        if not await self.bot.permissions.is_music_admin(interaction):
            return await interaction.response.send_message(
                "❌ У вас недостаточно прав для настройки бота",
                ephemeral=True
            )
        
        try:
            cursor = self.bot.db.conn.cursor()
            
            # Парсим роли
            admin_roles_list = []
            if admin_roles:
                for role_name in admin_roles.split(','):
                    role_name = role_name.strip()
                    role = discord.utils.get(interaction.guild.roles, name=role_name)
                    if role:
                        admin_roles_list.append(str(role.id))
            
            dj_roles_list = []
            if dj_roles:
                for role_name in dj_roles.split(','):
                    role_name = role_name.strip()
                    role = discord.utils.get(interaction.guild.roles, name=role_name)
                    if role:
                        dj_roles_list.append(str(role.id))
            
            # Проверяем существующие настройки
            cursor.execute(
                'SELECT guild_id FROM server_settings WHERE guild_id = ?',
                (str(interaction.guild.id),)
            )
            
            if cursor.fetchone():
                # Обновляем существующие настройки
                cursor.execute(
                    '''UPDATE server_settings 
                    SET admin_roles = ?, dj_roles = ?, max_queue_size = ?, default_volume = ?
                    WHERE guild_id = ?''',
                    (json.dumps(admin_roles_list) if admin_roles_list else None,
                     json.dumps(dj_roles_list) if dj_roles_list else None,
                     max_queue_size, default_volume, str(interaction.guild.id))
                )
            else:
                # Создаем новые настройки
                cursor.execute(
                    '''INSERT INTO server_settings 
                    (guild_id, admin_roles, dj_roles, max_queue_size, default_volume)
                    VALUES (?, ?, ?, ?, ?)''',
                    (str(interaction.guild.id),
                     json.dumps(admin_roles_list) if admin_roles_list else None,
                     json.dumps(dj_roles_list) if dj_roles_list else None,
                     max_queue_size, default_volume)
                )
            
            self.bot.db.conn.commit()
            
            embed = discord.Embed(
                title="⚙️ Настройки обновлены",
                color=0x00ff00
            )
            
            if admin_roles_list:
                embed.add_field(
                    name="Админ-роли",
                    value=', '.join([f"<@&{role_id}>" for role_id in admin_roles_list]),
                    inline=False
                )
            
            if dj_roles_list:
                embed.add_field(
                    name="DJ-роли", 
                    value=', '.join([f"<@&{role_id}>" for role_id in dj_roles_list]),
                    inline=False
                )
            
            embed.add_field(name="Макс. очередь", value=str(max_queue_size), inline=True)
            embed.add_field(name="Громкость", value=f"{default_volume*100}%", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ошибка при настройке: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="music_stats", description="Статистика бота")
    async def music_stats(self, interaction: discord.Interaction):
        """Показывает статистику бота"""
        
        embed = discord.Embed(title="📊 Статистика бота", color=0x0099ff)
        
        # Основная статистика
        embed.add_field(
            name="Сервера",
            value=f"```{len(self.bot.guilds)}```",
            inline=True
        )
        embed.add_field(
            name="Пользователи", 
            value=f"```{len(self.bot.users)}```",
            inline=True
        )
        embed.add_field(
            name="Активные плееры",
            value=f"```{len(self.bot.players)}```",
            inline=True
        )
        
        # Пинг
        embed.add_field(
            name="Пинг",
            value=f"```{round(self.bot.latency * 1000)}ms```",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="force_leave", description="Принудительно отключить бота от голосового канала")
    async def force_leave(self, interaction: discord.Interaction):
        """Принудительно отключает бота от голосового канала"""
        
        if not await self.bot.permissions.is_music_admin(interaction):
            return await interaction.response.send_message(
                "❌ У вас недостаточно прав для этой команды",
                ephemeral=True
            )
        
        voice_client = interaction.guild.voice_client
        if not voice_client:
            return await interaction.response.send_message("❌ Бот не подключен к голосовому каналу")
        
        # Очищаем очередь
        player = self.bot.players.get(interaction.guild.id)
        if player:
            player.clear_queue()
            if voice_client.is_playing():
                voice_client.stop()
        
        await voice_client.disconnect()
        await interaction.response.send_message("✅ Бот отключен от голосового канала")

async def setup(bot):
    await bot.add_cog(AdminCog(bot))