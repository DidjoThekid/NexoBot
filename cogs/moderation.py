import discord
from discord.ext import commands
from discord.ext.commands import Cog, command
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("NexoBot")

class Moderation(Cog):
    """Commandes de modération"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "Aucune raison fournie"):
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Membre expulsé",
                description=f"{member.mention} a été kick du serveur.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de kick ce membre.")
    
    @command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "Aucune raison fournie"):
        try:
            await member.ban(reason=reason, delete_message_days=0)
            embed = discord.Embed(
                title="🔨 Membre banni",
                description=f"{member.mention} a été banni.",
                color=discord.Color.red()
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de ban ce membre.")
    
    @command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member: str):
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
                await ctx.send(f"✅ {member_found.mention} a été débanni.")
            else:
                await ctx.send("❌ Membre non trouvé dans les bannissements.")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount > 100:
            await ctx.send("❌ Tu ne peux pas supprimer plus de 100 messages.")
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
            msg = await ctx.send(f"✅ {len(deleted) - 1} message(s) supprimé(s).", delete_after=5)
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas la permission de supprimer des messages.")
    
    @command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: int, *, reason: str = "Aucune raison"):
        try:
            until = datetime.utcnow() + timedelta(minutes=duration)
            await member.timeout(until, reason=reason)
            await ctx.send(f"🔇 {member.mention} a été mute pour {duration} minute(s).")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    @command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        try:
            await member.timeout(None)
            await ctx.send(f"🔊 {member.mention} n'est plus mute.")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
