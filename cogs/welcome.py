import discord
from discord.ext import commands
from discord.ext.commands import Cog
import logging

logger = logging.getLogger("NexoBot")

class Welcome(Cog):
    """Système de bienvenue"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_member_join(self, member):
        welcome_channel_id = self.bot.config.get("welcome_channel_id")
        if not welcome_channel_id:
            return
        
        channel = member.guild.get_channel(welcome_channel_id)
        if not channel:
            return
        
        welcome_message = self.bot.config.get("welcome_message", "Bienvenue {mention} !")
        
        message = welcome_message.format(
            mention=member.mention,
            server=member.guild.name,
            count=len(member.guild.members),
            name=member.name
        )
        
        embed = discord.Embed(
            title="👋 Bienvenue !",
            description=message,
            color=discord.Color.green(),
            timestamp=member.joined_at
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        try:
            await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Erreur welcome: {e}")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
