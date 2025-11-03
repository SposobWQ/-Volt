import discord
from discord.ext import commands
from datetime import datetime
from core.logger import logger

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Вызывается при запуске бота"""
        logger.music(f"Бот {self.bot.user} готов к работе!")
        logger.info(f"Подключен к {len(self.bot.guilds)} серверам", "📊")
        
        # Устанавливаем статус бота
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="/help | музыку 🎵"
        )
        await self.bot.change_presence(activity=activity)
        logger.info("Статус бота установлен", "🎯")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Вызывается при добавлении бота на сервер"""
        logger.success(f"Добавлен на сервер: {guild.name} (ID: {guild.id}, Участников: {guild.member_count})", "✅")
        
        # Ищем канал для отправки приветственного сообщения
        system_channel = guild.system_channel
        if system_channel and system_channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title="🎵 Спасибо за добавление!",
                description="Я музыкальный бот с продвинутыми функциями.",
                color=0x00ff00
            )
            # ... остальной код приветственного сообщения ...
            await system_channel.send(embed=embed)
            logger.info(f"Отправлено приветственное сообщение на сервере: {guild.name}")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Вызывается при удалении бота с сервера"""
        logger.warning(f"Удален с сервера: {guild.name} (ID: {guild.id})", "❌")
        
        # Очищаем данные сервера из памяти
        if guild.id in self.bot.players:
            del self.bot.players[guild.id]
            logger.info(f"Очищены данные плеера для сервера: {guild.name}")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Автоматическое отключение при пустом канале"""
        if member.bot:
            return
        
        voice_client = member.guild.voice_client
        if voice_client and voice_client.is_connected():
            # Проверяем, остались ли в канале пользователи (не боты)
            if len([m for m in voice_client.channel.members if not m.bot]) == 0:
                player = self.bot.players.get(member.guild.id)
                if player:
                    player.clear_queue()
                    if voice_client.is_playing():
                        voice_client.stop()
                
                await voice_client.disconnect()
                logger.voice(f"Отключен от пустого канала на сервере: {member.guild.name}")
    
    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction, command):
        """Логирование выполнения slash-команд"""
        logger.command(
            user=f"{interaction.user.name} ({interaction.user.id})",
            command=command.name,
            guild=interaction.guild.name if interaction.guild else "DM",
            emoji="⚡"
        )
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Обработка ошибок команд"""
        if isinstance(error, commands.CommandNotFound):
            return  # Игнорируем неизвестные команды
        
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"❌ Мне не хватает прав: {', '.join(error.missing_permissions)}")
            logger.warning(f"Недостаточно прав: {error.missing_permissions}")
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ У вас недостаточно прав для этой команды")
            logger.warning(f"Пользователь {ctx.author} пытался использовать команду без прав")
        
        elif isinstance(error, commands.NotOwner):
            await ctx.send("❌ Эта команда доступна только владельцу бота")
        
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Эта команда не работает в личных сообщениях")
        
        else:
            logger.error(f"Необработанная ошибка: {error}")
            embed = discord.Embed(
                title="❌ Произошла ошибка",
                description="Попробуйте еще раз или обратитесь к администратору",
                color=0xff0000
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EventsCog(bot))
    logger.success("Модуль events загружен", "🔔")