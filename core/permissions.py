import json

class PermissionSystem:
    def __init__(self, db):
        self.db = db
    
    async def is_music_admin(self, interaction):
        if interaction.user.id == interaction.guild.owner_id:
            return True
        
        if interaction.user.guild_permissions.administrator:
            return True
        
        settings = self.db.get_guild_settings(interaction.guild.id)
        if settings and settings['admin_roles']:
            user_roles = [str(role.id) for role in interaction.user.roles]
            return any(role in settings['admin_roles'] for role in user_roles)
        
        return False
    
    async def is_dj(self, interaction):
        if await self.is_music_admin(interaction):
            return True
        
        settings = self.db.get_guild_settings(interaction.guild.id)
        if settings and settings['dj_roles']:
            user_roles = [str(role.id) for role in interaction.user.roles]
            return any(role in settings['dj_roles'] for role in user_roles)
        
        return False