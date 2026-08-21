import discord
from discord.ext import commands
from discord.ext.commands import Cog
import logging
from datetime import datetime

logger = logging.getLogger("NexoBot")

class Logs(Cog):
    """Système de logs du serveur"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_message_delete(self, message):
        """Log les messages supprimés"""
        if message.author.bot:
            return
        
        log_channel = self._get_log_channel(message.guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="🗑️ Message supprimé",
            description=f"Un message de {message.author.mention} a été supprimé dans {message.channel.mention}",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        
        if message.content:
            embed.add_field(name="Contenu", value=message.content[:1024], inline=False)
        
        if message.attachments:
            files = ", ".join([att.filename for att in message.attachments])
            embed.add_field(name="Pièces jointes", value=files, inline=False)
        
        embed.set_footer(text=f"ID: {message.id}", icon_url=message.author.avatar.url if message.author.avatar else None)
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Erreur log message delete: {e}")
    
    @Cog.listener()
    async def on_message_edit(self, before, after):
        """Log les messages édités"""
        if before.author.bot:
            return
        
        if before.content == after.content:
            return
        
        log_channel = self._get_log_channel(before.guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="✏️ Message édité",
            description=f"Un message de {before.author.mention} a été édité dans {before.channel.mention}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Avant", value=before.content[:1024] or "*Pas de contenu*", inline=False)
        embed.add_field(name="Après", value=after.content[:1024] or "*Pas de contenu*", inline=False)
        
        embed.set_footer(text=f"ID: {before.id}", icon_url=before.author.avatar.url if before.author.avatar else None)
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Erreur log message edit: {e}")
    
    @Cog.listener()
    async def on_member_join(self, member):
        """Log les nouveaux membres"""
        log_channel = self._get_log_channel(member.guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="👥 Nouveau membre",
            description=f"{member.mention} a rejoint le serveur",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y à %H:%M"), inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Membre n°", value=len(member.guild.members), inline=True)
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Erreur log member join: {e}")
    
    @Cog.listener()
    async def on_member_remove(self, member):
        """Log les départs"""
        log_channel = self._get_log_channel(member.guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="👤 Membre parti",
            description=f"{member.mention} a quitté le serveur",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Membre n°", value=len(member.guild.members), inline=True)
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Erreur log member remove: {e}")
    
    def _get_log_channel(self, guild):
        """Récupère le canal de logs"""
        log_channel_id = self.bot.config.get("log_channel_id")
        if log_channel_id:
            return guild.get_channel(log_channel_id)
        return None

def setup(bot):
    bot.add_cog(Logs(bot))
