import discord
from discord.ext import commands
from discord.ext.commands import Cog, command
import logging
import platform
import psutil
from datetime import datetime

logger = logging.getLogger("NexoBot")

class Utility(Cog):
    """Commandes utilitaires"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @command(name="ping")
    async def ping(self, ctx):
        """Affiche le ping du bot"""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title=" Pong !",
            description=f"Latence: **{latency}ms**",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @command(name="info")
    async def info(self, ctx):
        """Affiche les informations du bot"""
        embed = discord.Embed(
            title=" Informations de NexoBot",
            description="Votre serveur, simplifié.",
            color=discord.Color.purple()
        )
        embed.add_field(name="Serveurs", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Utilisateurs", value=len(self.bot.users), inline=True)
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)
        embed.set_footer(text=f"Bot créé par DidjoTheKid")
        await ctx.send(embed=embed)
    
    @command(name="serverinfo")
    async def serverinfo(self, ctx):
        """Affiche les informations du serveur"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f" Informations de {guild.name}",
            color=discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Propriétaire", value=guild.owner.mention, inline=True)
        embed.add_field(name="ID", value=guild.id, inline=True)
        embed.add_field(name="Créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Membres", value=len(guild.members), inline=True)
        embed.add_field(name="Canaux", value=len(guild.channels), inline=True)
        embed.add_field(name="Rôles", value=len(guild.roles), inline=True)
        embed.add_field(name="Emojis", value=len(guild.emojis), inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
        embed.add_field(name="Niveau de boost", value=guild.premium_tier, inline=True)
        
        embed.set_footer(text=f"ID: {guild.id}")
        await ctx.send(embed=embed)
    
    @command(name="userinfo")
    async def userinfo(self, ctx, member: discord.Member = None):
        """Affiche les informations d'un utilisateur"""
        if not member:
            member = ctx.author
        
        embed = discord.Embed(
            title=f"👤 Informations de {member.name}",
            color=member.color
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.add_field(name="Pseudo complet", value=member, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Statut", value=str(member.status).capitalize(), inline=True)
        embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="A rejoint le serveur le", value=member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "N/A", inline=True)
        embed.add_field(name="Rôles", value=len(member.roles) - 1, inline=True)
        
        if member.roles:
            roles = ", ".join([role.mention for role in member.roles[1:]])
            embed.add_field(name="Rôles", value=roles if roles else "Aucun", inline=False)
        
        embed.set_footer(text=f"ID: {member.id}")
        await ctx.send(embed=embed)
    
    @command(name="help")
    async def help_command(self, ctx):
        """Affiche l'aide du bot"""
        embed = discord.Embed(
            title=" Aide de NexoBot",
            description="Liste des commandes disponibles",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🔧 Modération",
            value="`!kick`, `!ban`, `!unban`, `!clear`, `!mute`, `!unmute`",
            inline=False
        )
        embed.add_field(
            name="🎫 Tickets",
            value="`!ticket`, `!close`",
            inline=False
        )
        embed.add_field(
            name="📊 Utilitaires",
            value="`!ping`, `!info`, `!serverinfo`, `!userinfo`",
            inline=False
        )
        
        embed.set_footer(text=f"Préfixe: {self.bot.command_prefix}")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Utility(bot))
