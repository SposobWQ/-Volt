import discord
from discord import app_commands
from discord.ext import commands

class SyncCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sync", description="Синхронизировать команды (только для владельца)")
    async def sync(self, interaction: discord.Interaction):
        """Синхронизирует slash-команды"""
        if interaction.user.id != self.bot.owner_id:
            return await interaction.response.send_message("❌ Эта команда только для владельца бота!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            synced = await self.bot.tree.sync()
            await interaction.followup.send(f"✅ Синхронизировано {len(synced)} команд!")
        except Exception as e:
            await interaction.followup.send(f"❌ Ошибка синхронизации: {e}")

async def setup(bot):
    await bot.add_cog(SyncCog(bot))