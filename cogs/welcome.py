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
        """Accueille les nouveaux membres"""
        welcome_channel_id = self.bot.config.get("welcome_channel_id")
        if not welcome_channel_id:
            return
        
        channel = member.guild.get_channel(welcome_channel_id)
        if not channel:
            return
        
        # Récupérer le message de bienvenue personnalisé
        welcome_message = self.bot.config.get("welcome_message", "Bienvenue {mention} sur **{server}** !")
        
        # Personnaliser le message
        message = welcome_message.format(
            mention=member.mention,
            server=member.guild.name,
            count=len(member.guild.members),
            name=member.name
        )
        
        # Créer l'embed de bienvenue
        embed = discord.Embed(
            title=" Bienvenue !",
            description=message,
            color=discord.Color.green(),
            timestamp=member.joined_at
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Membre n°", value=len(member.guild.members), inline=True)
        embed.set_footer(text=f"ID: {member.id}")
        
        try:
            await channel.send(embed=embed)
            logger.info(f"Message de bienvenue envoyé pour {member}")
        except Exception as e:
            logger.error(f"Erreur envoi welcome message: {e}")

def setup(bot):
    bot.add_cog(Welcome(bot))
