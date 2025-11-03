import discord
from discord import app_commands
from discord.ext import commands

class VoiceManagerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="set_voice_channel", description="Установить голосовой канал для автоподключения")
    @app_commands.describe(channel="Голосовой канал для автоподключения")
    async def set_voice_channel(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        """Устанавливает голосовой канал для автоподключения бота"""
        if not await self.bot.permissions.is_music_admin(interaction):
            return await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)
        
        try:
            cursor = self.bot.db.conn.cursor()
            cursor.execute(
                '''INSERT OR REPLACE INTO voice_settings 
                (guild_id, default_voice_channel_id, auto_connect) 
                VALUES (?, ?, ?)''',
                (str(interaction.guild.id), str(channel.id), True)
            )
            self.bot.db.conn.commit()
            
            await interaction.response.send_message(
                f"✅ Автоподключение установлено на канал: {channel.mention}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)
    
    @app_commands.command(name="auto_connect", description="Включить/выключить автоподключение")
    @app_commands.describe(enabled="Включить автоподключение")
    async def auto_connect(self, interaction: discord.Interaction, enabled: bool):
        """Включает/выключает автоподключение к голосовому каналу"""
        if not await self.bot.permissions.is_music_admin(interaction):
            return await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)
        
        try:
            cursor = self.bot.db.conn.cursor()
            cursor.execute(
                'UPDATE voice_settings SET auto_connect = ? WHERE guild_id = ?',
                (enabled, str(interaction.guild.id))
            )
            self.bot.db.conn.commit()
            
            status = "включено" if enabled else "выключено"
            await interaction.response.send_message(
                f"✅ Автоподключение {status}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)
    
    async def get_default_voice_channel(self, guild_id):
        """Получает голосовой канал для автоподключения"""
        try:
            cursor = self.bot.db.conn.cursor()
            cursor.execute(
                'SELECT default_voice_channel_id, auto_connect FROM voice_settings WHERE guild_id = ?',
                (str(guild_id),)
            )
            result = cursor.fetchone()
            
            if result and result[1]:  # auto_connect = True
                channel_id = result[0]
                guild = self.bot.get_guild(guild_id)
                if guild:
                    return guild.get_channel(int(channel_id))
            return None
        except:
            return None

async def setup(bot):
    await bot.add_cog(VoiceManagerCog(bot))