import discord
from discord.ext import commands
from discord.ext.commands import Cog, command
import logging

logger = logging.getLogger("NexoBot")

class Moderation(Cog):
    """Commandes de modération"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "Aucune raison fournie"):
        """Expulse un membre du serveur"""
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Membre expulsé",
                description=f"{member.mention} a été kick du serveur.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.set_footer(text=f"Action par {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            await ctx.send(embed=embed)
            logger.info(f"{ctx.author} a kick {member} pour: {reason}")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de kick ce membre.")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "Aucune raison fournie"):
        """Bannit un membre du serveur"""
        try:
            await member.ban(reason=reason, delete_message_days=0)
            embed = discord.Embed(
                title="🔨 Membre banni",
                description=f"{member.mention} a été banni du serveur.",
                color=discord.Color.red()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.set_footer(text=f"Action par {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            await ctx.send(embed=embed)
            logger.info(f"{ctx.author} a ban {member} pour: {reason}")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de ban ce membre.")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member: str):
        """Débannit un membre du serveur"""
        try:
            banned_users = await ctx.guild.bans()
            member_found = None
            
            for ban_entry in banned_users:
                user = ban_entry.user
                if user.name == member or str(user.id) == member:
                    member_found = user
                    break
            
            if member_found:
                await ctx.guild.unban(member_found)
                embed = discord.Embed(
                    title="✅ Membre débanni",
                    description=f"{member_found.mention} a été débanni.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                logger.info(f"{ctx.author} a unban {member_found}")
            else:
                await ctx.send("❌ Membre non trouvé dans la liste des bannissements.")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Supprime un nombre de messages"""
        if amount > 100:
            await ctx.send(" Tu ne peux pas supprimer plus de 100 messages à la fois.")
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
            msg = await ctx.send(f"✅ {len(deleted) - 1} message(s) supprimé(s).", delete_after=5)
            logger.info(f"{ctx.author} a supprimé {len(deleted) - 1} messages dans {ctx.channel}")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de supprimer des messages.")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: int, *, reason: str = "Aucune raison fournie"):
        """Rend un membre muet pour une durée en minutes"""
        try:
            from datetime import datetime, timedelta
            until = datetime.utcnow() + timedelta(minutes=duration)
            await member.timeout(until, reason=reason)
            embed = discord.Embed(
                title=" Membre mute",
                description=f"{member.mention} a été mute pour {duration} minute(s).",
                color=discord.Color.orange()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            await ctx.send(embed=embed)
            logger.info(f"{ctx.author} a mute {member} pour {duration} minutes")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "Aucune raison fournie"):
        """Enlève le mute d'un membre"""
        try:
            await member.timeout(None, reason=reason)
            embed = discord.Embed(
                title="🔊 Membre unmute",
                description=f"{member.mention} n'est plus mute.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            logger.info(f"{ctx.author} a unmute {member}")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

def setup(bot):
    bot.add_cog(Moderation(bot))
