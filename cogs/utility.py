import discord
from discord.ext import commands
from discord.ext.commands import Cog, command
import logging
import platform

logger = logging.getLogger("NexoBot")

class Utility(Cog):
    """Commandes utilitaires"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong !",
            description=f"Latence: **{latency}ms**",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @command(name="info")
    async def info(self, ctx):
        embed = discord.Embed(
            title=" NexoBot",
            description="Votre serveur, simplifié.",
            color=discord.Color.purple()
        )
        embed.add_field(name="Serveurs", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Utilisateurs", value=len(self.bot.users), inline=True)
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        await ctx.send(embed=embed)
    
    @command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📚 Aide",
            description="Commandes disponibles",
            color=discord.Color.blue()
        )
        embed.add_field(name="Modération", value="`!kick`, `!ban`, `!clear`, `!mute`", inline=False)
        embed.add_field(name="Tickets", value="`!ticket`, `!close`", inline=False)
        embed.add_field(name="Utilitaires", value="`!ping`, `!info`, `!help`", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
