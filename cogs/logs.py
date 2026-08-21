import discord
from discord.ext import commands
from discord.ext.commands import Cog
import logging
from datetime import datetime

logger = logging.getLogger("NexoBot")

class Logs(Cog):
    """Système de logs"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        
        log_channel = self._get_log_channel(message.guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="🗑️ Message supprimé",
            description=f"Message de {message.author.mention} dans {message.channel.mention}",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        
        if message.content:
            embed.add_field(name="Contenu", value=message.content[:1024], inline=False)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        
        log_channel = self._get_log_channel(before.guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="️ Message édité",
            description=f"{before.author.mention} dans {before.channel.mention}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Avant", value=before.content[:512] or "*Vide*", inline=False)
        embed.add_field(name="Après", value=after.content[:512] or "*Vide*", inline=False)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @Cog.listener()
    async def on_member_join(self, member):
        log_channel = self._get_log_channel(member.guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="👥 Nouveau membre",
            description=f"{member.mention} a rejoint",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @Cog.listener()
    async def on_member_remove(self, member):
        log_channel = self._get_log_channel(member.guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="👤 Membre parti",
            description=f"{member.mention} a quitté",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    def _get_log_channel(self, guild):
        log_channel_id = self.bot.config.get("log_channel_id")
        if log_channel_id:
            return guild.get_channel(log_channel_id)
        return None

async def setup(bot):
    await bot.add_cog(Logs(bot))
